from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from Models.notifications.models import DeviceToken
from Models.users.models import User


def make_user(username: str) -> User:
    return User.objects.create(
        username=username,
        email=f'{username}@test.com',
        firebase_uid=f'uid_{username}',
    )


class DeviceTokenApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('alice')
        self.other = make_user('bob')
        self.url = reverse('device-token')

    def test_unauthenticated_is_rejected(self):
        resp = self.client.post(self.url, {'token': 't1', 'platform': 'android'})
        self.assertIn(resp.status_code, (401, 403))
        self.assertEqual(DeviceToken.objects.count(), 0)

    def test_register_new_token(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.url, {'token': 't1', 'platform': 'android'})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(DeviceToken.objects.get(token='t1').user, self.user)

    def test_register_same_token_twice_does_not_duplicate(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {'token': 't1', 'platform': 'android'})
        resp = self.client.post(self.url, {'token': 't1', 'platform': 'android'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(DeviceToken.objects.filter(token='t1').count(), 1)

    def test_register_token_owned_by_other_user_reassigns(self):
        DeviceToken.objects.create(user=self.other, token='t1', platform='android')
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {'token': 't1', 'platform': 'android'})
        self.assertEqual(DeviceToken.objects.get(token='t1').user, self.user)

    def test_register_invalid_platform(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.url, {'token': 't1', 'platform': 'windows'})
        self.assertEqual(resp.status_code, 400)

    def test_register_empty_token(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.url, {'token': '', 'platform': 'android'})
        self.assertEqual(resp.status_code, 400)

    def test_delete_own_token(self):
        DeviceToken.objects.create(user=self.user, token='t1', platform='android')
        self.client.force_authenticate(user=self.user)
        resp = self.client.delete(self.url, {'token': 't1'}, format='json')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(DeviceToken.objects.filter(token='t1').exists())

    def test_delete_token_of_other_user_is_noop(self):
        DeviceToken.objects.create(user=self.other, token='t1', platform='android')
        self.client.force_authenticate(user=self.user)
        resp = self.client.delete(self.url, {'token': 't1'}, format='json')
        self.assertEqual(resp.status_code, 204)
        self.assertTrue(DeviceToken.objects.filter(token='t1').exists())

    def test_delete_unknown_token_is_noop(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.delete(self.url, {'token': 'nope'}, format='json')
        self.assertEqual(resp.status_code, 204)


# --- notify_user (FCM mocked) ------------------------------------------------

from unittest.mock import patch
from firebase_admin import messaging
from Models.notifications.services import notify_user


class NotifyUserTests(TestCase):
    def setUp(self):
        self.user = make_user('alice')

    @patch('Models.notifications.services.messaging.send')
    def test_sends_one_message_per_token(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='t1', platform='android')
        DeviceToken.objects.create(user=self.user, token='t2', platform='android')
        notify_user(self.user, 'Title', 'Body', {'space_id': 5})
        self.assertEqual(mock_send.call_count, 2)

    @patch('Models.notifications.services.messaging.send')
    def test_no_tokens_sends_nothing(self, mock_send):
        notify_user(self.user, 'Title', 'Body')
        mock_send.assert_not_called()

    @patch('Models.notifications.services.messaging.send')
    def test_unregistered_token_is_pruned(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='dead', platform='android')
        DeviceToken.objects.create(user=self.user, token='live', platform='android')
        mock_send.side_effect = [messaging.UnregisteredError('gone'), 'ok']
        notify_user(self.user, 'Title', 'Body')
        self.assertFalse(DeviceToken.objects.filter(token='dead').exists())
        self.assertTrue(DeviceToken.objects.filter(token='live').exists())

    @patch('Models.notifications.services.messaging.send')
    def test_message_carries_token_text_and_stringified_data(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='t1', platform='android')
        notify_user(self.user, 'Title', 'Body', {'space_id': 5})
        message = mock_send.call_args.args[0]
        self.assertEqual(message.token, 't1')
        self.assertEqual(message.notification.title, 'Title')
        self.assertEqual(message.notification.body, 'Body')
        # FCM requires string values in the data payload.
        self.assertEqual(message.data, {'space_id': '5'})

    @patch('Models.notifications.services.messaging.send')
    def test_only_recipients_tokens_are_used(self, mock_send):
        other = make_user('bob')
        DeviceToken.objects.create(user=self.user, token='mine', platform='android')
        DeviceToken.objects.create(user=other, token='theirs', platform='android')
        notify_user(self.user, 'Title', 'Body')
        sent_tokens = [c.args[0].token for c in mock_send.call_args_list]
        self.assertEqual(sent_tokens, ['mine'])

    @patch('Models.notifications.services.messaging.send')
    def test_sender_id_mismatch_token_is_pruned(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='foreign', platform='android')
        mock_send.side_effect = messaging.SenderIdMismatchError('mismatch')
        notify_user(self.user, 'Title', 'Body')
        self.assertFalse(DeviceToken.objects.filter(token='foreign').exists())

    @patch('Models.notifications.services.messaging.send', side_effect=Exception('FCM down'))
    def test_outage_does_not_raise_and_keeps_token(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='t1', platform='android')
        notify_user(self.user, 'Title', 'Body')
        self.assertTrue(DeviceToken.objects.filter(token='t1').exists())


# --- send_test_push command ---------------------------------------------------

from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError


class SendTestPushCommandTests(TestCase):
    def setUp(self):
        self.user = make_user('alice')

    def run_command(self, identifier):
        out = StringIO()
        call_command('send_test_push', identifier, stdout=out)
        return out.getvalue()

    def test_unknown_user_raises(self):
        with self.assertRaises(CommandError):
            self.run_command('nobody')

    def test_user_without_devices_raises_with_hint(self):
        with self.assertRaisesMessage(CommandError, 'no registered devices'):
            self.run_command('alice')

    @patch('Models.notifications.management.commands.send_test_push.messaging.send')
    def test_sends_to_each_device_by_username_or_email(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='tok-aaaaaa', platform='android')
        out = self.run_command('alice')
        self.assertIn('1/1 sent', out)
        self.assertEqual(mock_send.call_args.args[0].token, 'tok-aaaaaa')
        self.run_command('alice@test.com')
        self.assertEqual(mock_send.call_count, 2)

    @patch('Models.notifications.management.commands.send_test_push.messaging.send', side_effect=Exception('403 permission denied'))
    def test_failure_is_reported_and_exits_non_zero_without_deleting_token(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='tok-aaaaaa', platform='android')
        with self.assertRaises(CommandError):
            self.run_command('alice')
        self.assertTrue(DeviceToken.objects.filter(token='tok-aaaaaa').exists())

    @patch('Models.notifications.management.commands.send_test_push.messaging.send')
    def test_full_token_is_not_printed(self, mock_send):
        DeviceToken.objects.create(user=self.user, token='secret-token-abcdef', platform='android')
        out = self.run_command('alice')
        self.assertNotIn('secret-token-abcdef', out)
        self.assertIn('abcdef', out)
