"""
Account deletion: DELETE /api/v1/user/

Covers the recent-login guard, leaving spaces like a manual leave would (admin promotion,
creator transfer, empty-space removal), cascading personal data, pending invites, and the
Firebase deletion being part of the same all-or-nothing operation.
"""
import time
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import UnknownError
from rest_framework.test import APIClient

from Models.habits.models import BaseHabit
from Models.notifications.models import DeviceToken
from Models.spaces.models import PendingInvite, Space, SpaceRole
from Models.users.models import User

DELETE_FIREBASE = 'Models.users.api.api.firebase_auth.delete_user'


def make_user(username, anonymous=False) -> User:
    return User.objects.create(
        username=username,
        email=f'{username}@anonymous.firebase' if anonymous else f'{username}@test.com',
        firebase_uid=f'uid_{username}',
        is_anonymous_firebase_user=anonymous,
    )


def make_space(creator: User, name='Space') -> Space:
    space = Space.objects.create(creator=creator, name=name)
    SpaceRole.objects.create(member=creator, space=space, role='admin')
    return space


def client_for(user: User, auth_age_seconds=10) -> APIClient:
    """Client authenticated as `user` whose Firebase token says it signed in `auth_age_seconds` ago."""
    client = APIClient()
    client.force_authenticate(user=user, token={'uid': user.firebase_uid, 'auth_time': int(time.time()) - auth_age_seconds})
    return client


class AccountDeletionTests(TestCase):
    def setUp(self):
        self.url = reverse('user')
        self.user = make_user('leaver')

    @patch(DELETE_FIREBASE)
    def test_deletes_user_and_firebase_account(self, mock_delete_firebase):
        resp = client_for(self.user).delete(self.url)

        self.assertEqual(resp.status_code, 204)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        mock_delete_firebase.assert_called_once_with('uid_leaver')

    def test_requires_authentication(self):
        resp = APIClient().delete(self.url)
        self.assertIn(resp.status_code, (401, 403))

    # ---- recent login guard ----

    @patch(DELETE_FIREBASE)
    def test_registered_user_with_stale_login_is_rejected(self, mock_delete_firebase):
        resp = client_for(self.user, auth_age_seconds=3600).delete(self.url)

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['code'], 'recent_login_required')
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        mock_delete_firebase.assert_not_called()

    @patch(DELETE_FIREBASE)
    def test_registered_user_without_auth_time_is_rejected(self, mock_delete_firebase):
        client = APIClient()
        client.force_authenticate(user=self.user)
        resp = client.delete(self.url)

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['code'], 'recent_login_required')
        mock_delete_firebase.assert_not_called()

    @patch(DELETE_FIREBASE)
    def test_anonymous_user_does_not_need_recent_login(self, mock_delete_firebase):
        anon = make_user('guest', anonymous=True)
        resp = client_for(anon, auth_age_seconds=10 ** 6).delete(self.url)

        self.assertEqual(resp.status_code, 204)
        self.assertFalse(User.objects.filter(pk=anon.pk).exists())
        mock_delete_firebase.assert_called_once_with('uid_guest')

    # ---- Firebase failure handling ----

    @patch(DELETE_FIREBASE, side_effect=UnknownError('firebase down'))
    def test_firebase_failure_rolls_everything_back(self, _mock):
        space = make_space(self.user)
        user_pk = self.user.pk  # Django clears pk on the in-memory instance when it is deleted

        resp = client_for(self.user).delete(self.url)

        self.assertEqual(resp.status_code, 502)
        self.assertTrue(User.objects.filter(pk=user_pk).exists())
        self.assertTrue(Space.objects.filter(pk=space.pk).exists())
        self.assertTrue(SpaceRole.objects.filter(member_id=user_pk, space=space).exists())

    @patch(DELETE_FIREBASE, side_effect=firebase_auth.UserNotFoundError('gone'))
    def test_firebase_user_already_gone_is_treated_as_success(self, _mock):
        resp = client_for(self.user).delete(self.url)

        self.assertEqual(resp.status_code, 204)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    @patch(DELETE_FIREBASE)
    def test_user_without_firebase_uid_skips_firebase(self, mock_delete_firebase):
        legacy = User.objects.create(username='legacy', email='legacy@test.com', firebase_uid=None)
        resp = client_for(legacy).delete(self.url)

        self.assertEqual(resp.status_code, 204)
        mock_delete_firebase.assert_not_called()

    # ---- spaces ----

    @patch(DELETE_FIREBASE)
    def test_space_with_only_this_user_is_deleted(self, _mock):
        space = make_space(self.user)

        client_for(self.user).delete(self.url)

        self.assertFalse(Space.objects.filter(pk=space.pk).exists())

    @patch(DELETE_FIREBASE)
    def test_space_survives_with_new_admin_and_no_creator_when_others_remain(self, _mock):
        other = make_user('stayer')
        space = make_space(self.user)
        SpaceRole.objects.create(member=other, space=space, role='member')

        client_for(self.user).delete(self.url)

        space.refresh_from_db()
        self.assertIsNone(space.creator)
        self.assertEqual(SpaceRole.objects.get(space=space, member=other).role, 'admin')
        self.assertEqual(space.members.count(), 1)

    @patch(DELETE_FIREBASE)
    def test_leaves_every_space_the_user_belongs_to(self, _mock):
        other = make_user('owner')
        joined = make_space(other, name='Joined')
        SpaceRole.objects.create(member=self.user, space=joined, role='member')
        mine = make_space(self.user, name='Mine')

        client_for(self.user).delete(self.url)

        self.assertTrue(Space.objects.filter(pk=joined.pk).exists())
        self.assertFalse(SpaceRole.objects.filter(space=joined, member_id=self.user.pk).exists())
        self.assertFalse(Space.objects.filter(pk=mine.pk).exists())

    @patch(DELETE_FIREBASE)
    def test_member_space_habits_are_deleted_but_other_members_are_untouched(self, _mock):
        other = make_user('owner')
        space = make_space(other)
        SpaceRole.objects.create(member=self.user, space=space, role='member')
        other_habit = BaseHabit.objects.create(owner=other, title='Other habit')
        other_habit.spaces.add(space)
        my_habit = BaseHabit.objects.create(owner=self.user, title='My habit')
        my_habit.spaces.add(space)

        client_for(self.user).delete(self.url)

        self.assertFalse(BaseHabit.objects.filter(pk=my_habit.pk).exists())
        self.assertTrue(BaseHabit.objects.filter(pk=other_habit.pk).exists())

    # ---- other personal data ----

    @patch(DELETE_FIREBASE)
    def test_personal_habits_and_device_tokens_are_removed(self, _mock):
        habit = BaseHabit.objects.create(owner=self.user, title='Solo habit')
        token = DeviceToken.objects.create(user=self.user, token='fcm-token')

        client_for(self.user).delete(self.url)

        self.assertFalse(BaseHabit.objects.filter(pk=habit.pk).exists())
        self.assertFalse(DeviceToken.objects.filter(pk=token.pk).exists())

    @patch(DELETE_FIREBASE)
    def test_pending_invites_for_the_users_email_are_removed(self, _mock):
        other = make_user('inviter')
        space = make_space(other)
        mine = PendingInvite.objects.create(email='LEAVER@test.com', space=space, invited_by=other)
        someone_elses = PendingInvite.objects.create(email='else@test.com', space=space, invited_by=other)

        client_for(self.user).delete(self.url)

        self.assertFalse(PendingInvite.objects.filter(pk=mine.pk).exists())
        self.assertTrue(PendingInvite.objects.filter(pk=someone_elses.pk).exists())

    @patch(DELETE_FIREBASE)
    def test_invites_sent_by_the_deleted_user_are_kept_with_no_inviter(self, _mock):
        other = make_user('owner')
        space = make_space(other)
        SpaceRole.objects.create(member=self.user, space=space, role='admin')
        invite = PendingInvite.objects.create(email='new@test.com', space=space, invited_by=self.user)

        client_for(self.user).delete(self.url)

        invite.refresh_from_db()
        self.assertIsNone(invite.invited_by)

    @patch(DELETE_FIREBASE)
    def test_does_not_affect_other_users(self, _mock):
        other = make_user('bystander')

        client_for(self.user).delete(self.url)

        self.assertTrue(User.objects.filter(pk=other.pk).exists())
