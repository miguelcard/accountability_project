"""
End-to-end checks for "usernames are case-insensitive and stored lowercase".

Covers: model normalisation, DB constraint, user PATCH/PUT API, the data
migration, username/email availability check, user search, adding members to a
space (by username and by email), pending invites, Firebase user creation and
the send_test_push command.
"""
from importlib import import_module
from io import StringIO
from unittest.mock import patch

from django.apps import apps as django_apps
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from firebase.authentication import FirebaseAuthentication
from Models.notifications.models import DeviceToken
from Models.spaces.models import PendingInvite, Space, SpaceRole
from Models.users.models import User


def make_user(username, email=None) -> User:
    return User.objects.create(
        username=username,
        email=email or f'{(username or "nouser").lower()}@test.com',
        firebase_uid=f'uid_{username}',
    )


def make_space(creator: User) -> Space:
    space = Space.objects.create(creator=creator, name='Test Space')
    SpaceRole.objects.create(member=creator, space=space, role='admin')
    return space


# ─── Model ───────────────────────────────────────────────────────────────────

class UsernameStoredLowercaseTests(TestCase):
    def test_save_lowercases_username(self):
        user = make_user('MiGgY')
        user.refresh_from_db()
        self.assertEqual(user.username, 'miggy')

    def test_save_strips_whitespace(self):
        user = make_user('  miggy ')
        user.refresh_from_db()
        self.assertEqual(user.username, 'miggy')

    def test_changing_username_on_existing_user_lowercases_it(self):
        user = make_user('miggy')
        user.username = 'NewName'
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.username, 'newname')

    def test_save_with_empty_or_null_username_does_not_crash(self):
        no_username = User.objects.create(username=None, email='n1@test.com', firebase_uid='uid_n1')
        blank = User.objects.create(username='', email='n2@test.com', firebase_uid='uid_n2')
        self.assertIsNone(User.objects.get(pk=no_username.pk).username)
        self.assertEqual(User.objects.get(pk=blank.pk).username, '')

    def test_saving_a_second_user_with_case_only_difference_fails(self):
        make_user('miggy')
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_user('MIGGY', 'other@test.com')

    def test_db_blocks_case_only_duplicate_username_even_when_save_is_bypassed(self):
        make_user('miggy')
        other = make_user('other')
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.filter(pk=other.pk).update(username='MIGGY')

    def test_db_blocks_uppercase_username_even_when_save_is_bypassed(self):
        user = make_user('miggy')
        with self.assertRaisesMessage(IntegrityError, 'user_username_is_lowercase'), transaction.atomic():
            User.objects.filter(pk=user.pk).update(username='Miggy')

    def test_db_blocks_bulk_created_uppercase_username(self):
        with self.assertRaisesMessage(IntegrityError, 'user_username_is_lowercase'), transaction.atomic():
            User.objects.bulk_create([User(username='Upper', email='u@test.com', firebase_uid='uid_u')])

    def test_db_blocks_case_only_duplicate_email(self):
        make_user('first', 'Same@Test.com')
        with self.assertRaisesMessage(IntegrityError, 'user_email_ci_unique'), transaction.atomic():
            make_user('second', 'same@test.com')

    def test_users_without_email_or_username_can_coexist(self):
        User.objects.create(username=None, email=None, firebase_uid='uid_x1')
        User.objects.create(username=None, email=None, firebase_uid='uid_x2')
        self.assertEqual(User.objects.filter(username__isnull=True).count(), 2)


# ─── User PATCH / PUT API ────────────────────────────────────────────────────

class UserUpdateUsernameTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('fb_placeholder')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('user')

    def test_patch_stores_lowercase(self):
        resp = self.client.patch(self.url, {'username': 'MiGgY'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['username'], 'miggy')
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'miggy')

    def test_patch_strips_whitespace(self):
        resp = self.client.patch(self.url, {'username': '  Miggy  '}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'miggy')

    def test_patch_case_only_duplicate_is_rejected_with_400(self):
        make_user('miggy')
        resp = self.client.patch(self.url, {'username': 'Miggy'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('username', resp.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'fb_placeholder')

    def test_patch_exact_duplicate_is_rejected_with_400(self):
        make_user('miggy')
        resp = self.client.patch(self.url, {'username': 'miggy'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_patch_own_username_with_different_case_is_allowed(self):
        self.client.patch(self.url, {'username': 'miggy'}, format='json')
        resp = self.client.patch(self.url, {'username': 'MIGGY'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'miggy')

    def test_patch_other_field_does_not_touch_username(self):
        resp = self.client.patch(self.url, {'name': 'Some Name'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'fb_placeholder')

    def test_put_stores_lowercase_and_rejects_case_only_duplicate(self):
        resp = self.client.put(self.url, {'username': 'MiGgY'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'miggy')

        other = make_user('someone_else')
        self.client.force_authenticate(user=other)
        resp = self.client.put(self.url, {'username': 'MIGGY'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_patch_rejects_usernames_breaking_the_format_rules(self):
        invalid = {
            'too short': 'ab',
            'too long': 'a' * 21,
            'space': 'has space',
            'symbol': 'bad!',
            'at sign': 'me@x.com',
            'non-ascii': 'İstanbul',
            'accent': 'josé',
            'blank': '',
            'reserved prefix': 'fb_sneaky',
            'reserved prefix uppercase': 'FB_Sneaky',
        }
        for label, value in invalid.items():
            with self.subTest(label):
                resp = self.client.patch(self.url, {'username': value}, format='json')
                self.assertEqual(resp.status_code, 400, resp.data)
                self.assertIn('username', resp.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'fb_placeholder')

    def test_patch_accepts_usernames_at_the_format_boundaries(self):
        for value in ('abc', 'a' * 20, 'a-b_c9', '123', 'x_y-z'):
            with self.subTest(value):
                resp = self.client.patch(self.url, {'username': value}, format='json')
                self.assertEqual(resp.status_code, 200, resp.data)
                self.user.refresh_from_db()
                self.assertEqual(self.user.username, value)

    def test_unchanged_legacy_username_does_not_block_other_edits(self):
        # Placeholder (fb_) and old-style names break today's rules but must stay editable around.
        User.objects.filter(pk=self.user.pk).update(username='fb_legacy_name_that_is_way_too_long')
        self.user.refresh_from_db()
        resp = self.client.patch(
            self.url, {'username': 'fb_legacy_name_that_is_way_too_long', 'name': 'New Name'}, format='json',
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'New Name')

    def test_losing_a_race_against_the_db_constraint_returns_400_not_500(self):
        # Simulates two simultaneous requests: validators pass, then the DB constraint rejects the write.
        with patch.object(User, 'save', side_effect=IntegrityError('duplicate key')):
            resp = self.client.patch(self.url, {'username': 'miggy'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('username', resp.data)


# ─── Availability check ──────────────────────────────────────────────────────

class CheckUsernameEmailExistsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('check-user-exists')
        make_user('miggy', 'Miggy@Test.com')

    def test_username_check_is_case_insensitive(self):
        for value in ('miggy', 'Miggy', 'MIGGY', ' miggy '):
            resp = self.client.get(self.url, {'username': value})
            self.assertTrue(resp.data['username_taken'], value)

    def test_email_check_is_case_insensitive_against_mixed_case_stored_email(self):
        for value in ('miggy@test.com', 'Miggy@Test.com', 'MIGGY@TEST.COM'):
            resp = self.client.get(self.url, {'email': value})
            self.assertTrue(resp.data['email_taken'], value)

    def test_unknown_username_and_email_not_taken(self):
        resp = self.client.get(self.url, {'username': 'nobody', 'email': 'nobody@test.com'})
        self.assertFalse(resp.data['username_taken'])
        self.assertFalse(resp.data['email_taken'])

    def test_no_params_returns_false_for_both(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.data, {'email_taken': False, 'username_taken': False})


# ─── Suggestions / search ────────────────────────────────────────────────────

class UsernameSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=make_user('searcher'))
        self.url = reverse('search-user')
        make_user('miggy')
        make_user('other_person')

    def _search(self, term):
        return [r['username'] for r in self.client.get(self.url, {'search': term}).data['results']]

    def test_search_ignores_case_of_the_typed_term(self):
        for term in ('miggy', 'Miggy', 'MIGGY', 'MiG'):
            self.assertIn('miggy', self._search(term), term)

    def test_search_does_not_return_non_matching_users(self):
        self.assertNotIn('other_person', self._search('miggy'))

    def test_blank_search_returns_nothing(self):
        self.assertEqual(self._search('   '), [])

    def test_returned_usernames_are_lowercase(self):
        for username in self._search('i'):
            self.assertEqual(username, username.lower())


# ─── Data migration ──────────────────────────────────────────────────────────

class LowercaseUsernamesMigrationTests(TestCase):
    def setUp(self):
        self.migration = import_module('Models.users.migrations.0012_lowercase_usernames')
        # The username constraints added by later migrations would reject the "old" rows these tests
        # simulate, so drop them inside this test's transaction (rolled back afterwards).
        with connection.schema_editor() as editor:
            for constraint in User._meta.constraints:
                if constraint.name.startswith('user_username_'):
                    editor.remove_constraint(User, constraint)

    def _run(self):
        self.migration.lowercase_usernames(django_apps, None)

    def test_lowercases_mixed_case_usernames(self):
        a, b = make_user('a_user'), make_user('b_user')
        User.objects.filter(pk=a.pk).update(username='Miggy')
        User.objects.filter(pk=b.pk).update(username='  ALREADY_UPPER')

        self._run()

        self.assertEqual(User.objects.get(pk=a.pk).username, 'miggy')
        self.assertEqual(User.objects.get(pk=b.pk).username, 'already_upper')

    def test_leaves_lowercase_null_and_blank_usernames_untouched(self):
        ok = make_user('fine')
        null_user = User.objects.create(username=None, email='n@test.com', firebase_uid='uid_n')
        blank_user = User.objects.create(username='', email='b@test.com', firebase_uid='uid_b')

        self._run()

        self.assertEqual(User.objects.get(pk=ok.pk).username, 'fine')
        self.assertIsNone(User.objects.get(pk=null_user.pk).username)
        self.assertEqual(User.objects.get(pk=blank_user.pk).username, '')

    def test_aborts_and_changes_nothing_when_usernames_would_collide(self):
        a, b, c = make_user('first'), make_user('second'), make_user('third')
        User.objects.filter(pk=a.pk).update(username='Miggy')
        User.objects.filter(pk=b.pk).update(username='miggy')
        User.objects.filter(pk=c.pk).update(username='OTHER')

        with self.assertRaisesMessage(RuntimeError, 'would collide'):
            self._run()

        self.assertEqual(User.objects.get(pk=a.pk).username, 'Miggy')
        self.assertEqual(User.objects.get(pk=b.pk).username, 'miggy')
        self.assertEqual(User.objects.get(pk=c.pk).username, 'OTHER')


# ─── Adding members to a space ───────────────────────────────────────────────

class AddMemberCaseInsensitiveTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_user('admin')
        self.space = make_space(self.admin)
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('spacerole-invite')

    def _invite(self, value):
        return self.client.post(self.url, {'username_email': value, 'role': 'member', 'space': self.space.id})

    def _is_member(self, user):
        return SpaceRole.objects.filter(member=user, space=self.space).exists()

    def test_username_in_any_case_adds_the_user(self):
        member = make_user('miggy')
        for typed in ('miggy', 'Miggy', 'MIGGY', ' miGGy '):
            with self.subTest(typed=typed):
                SpaceRole.objects.filter(member=member).delete()
                resp = self._invite(typed)
                self.assertEqual(resp.status_code, 201, resp.data)
                self.assertTrue(self._is_member(member))

    def test_unknown_username_returns_400_with_message(self):
        resp = self._invite('Nobody')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('username_email', resp.data)

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_existing_email_in_any_case_adds_the_user_without_creating_an_invite(self, mock_send):
        member = make_user('mixed', 'Mixed.Case@Test.com')
        for typed in ('mixed.case@test.com', 'MIXED.CASE@TEST.COM', 'Mixed.Case@Test.com'):
            with self.subTest(typed=typed):
                SpaceRole.objects.filter(member=member).delete()
                resp = self._invite(typed)
                self.assertEqual(resp.status_code, 201, resp.data)
                self.assertTrue(self._is_member(member))
        self.assertFalse(PendingInvite.objects.exists())
        mock_send.assert_not_called()

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_unknown_email_creates_pending_invite_stored_lowercase(self, mock_send):
        resp = self._invite('  NewPerson@Example.COM ')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['invited'])
        invite = PendingInvite.objects.get()
        self.assertEqual(invite.email, 'newperson@example.com')
        self.assertEqual(mock_send.call_args.kwargs['to_email'], 'newperson@example.com')

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_reinviting_with_different_case_keeps_a_single_pending_invite(self, mock_send):
        for typed in ('NewPerson@Example.com', 'newperson@example.com', 'NEWPERSON@EXAMPLE.COM'):
            self._invite(typed)
        self.assertEqual(PendingInvite.objects.filter(space=self.space).count(), 1)
        self.assertEqual(mock_send.call_count, 3)

    def test_non_member_cannot_add_members_even_with_valid_case_insensitive_name(self):
        make_user('miggy')
        outsider = make_user('outsider')
        self.client.force_authenticate(user=outsider)
        resp = self._invite('MIGGY')
        self.assertIn(resp.status_code, (400, 403))
        self.assertFalse(SpaceRole.objects.filter(member__username='miggy').exists())


class AcceptInviteEmailCaseTests(TestCase):
    def test_user_with_mixed_case_email_can_accept_invite_stored_lowercase(self):
        admin = make_user('admin')
        space = make_space(admin)
        invite = PendingInvite.objects.create(email='joiner@test.com', space=space, invited_by=admin)
        joiner = make_user('joiner', 'Joiner@Test.com')

        client = APIClient()
        client.force_authenticate(user=joiner)
        resp = client.post(reverse('invite-accept'), {'token': str(invite.token)})

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(SpaceRole.objects.filter(member=joiner, space=space).exists())


# ─── Firebase auto-created users ─────────────────────────────────────────────

class FirebasePlaceholderUsernameTests(TestCase):
    def _token(self, uid, provider='anonymous'):
        return {'uid': uid, 'email': '', 'firebase': {'sign_in_provider': provider}}

    def test_placeholder_username_is_lowercase_even_for_mixed_case_uid(self):
        user = FirebaseAuthentication._get_or_create_user(self._token('AbCdEfGhIjKlMnOpQrStUvWxYz12'))
        self.assertEqual(user.username, 'fb_abcdefghijklmnopqrst')

    def test_returning_user_keeps_the_same_row(self):
        token = self._token('AbCdEfGhIjKlMnOpQrStUvWxYz12')
        first = FirebaseAuthentication._get_or_create_user(token)
        second = FirebaseAuthentication._get_or_create_user(token)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(User.objects.count(), 1)

    def test_placeholder_user_can_then_choose_a_username(self):
        user = FirebaseAuthentication._get_or_create_user(self._token('UidWithCaps1234567890XYZ'))
        client = APIClient()
        client.force_authenticate(user=user)
        resp = client.patch(reverse('user'), {'username': 'Miggy'}, format='json')
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.username, 'miggy')


# ─── send_test_push command ──────────────────────────────────────────────────

class SendTestPushCaseTests(TestCase):
    def setUp(self):
        self.user = make_user('alice', 'Alice@Test.com')
        DeviceToken.objects.create(user=self.user, token='tok-aaaaaa', platform='android')

    @patch('Models.notifications.management.commands.send_test_push.messaging.send')
    def test_finds_user_by_username_or_email_in_any_case(self, mock_send):
        for identifier in ('ALICE', 'Alice', 'alice@test.com', 'ALICE@TEST.COM'):
            call_command('send_test_push', identifier, stdout=StringIO())
        self.assertEqual(mock_send.call_count, 4)
