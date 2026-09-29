from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from Models.users.models import User
from .models import Space, SpaceRole, PendingInvite, MAX_CREATED_SPACES_PER_USER


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_user(username: str, email: str, anonymous: bool = False) -> User:
    return User.objects.create(
        username=username,
        email=email,
        firebase_uid=f'uid_{username}',
        is_anonymous_firebase_user=anonymous,
    )


def make_space(creator: User, name: str = 'Test Space') -> Space:
    space = Space.objects.create(creator=creator, name=name)
    SpaceRole.objects.create(member=creator, space=space, role='admin')
    return space


# ─── Existing space creation limit tests ─────────────────────────────────────

class SpaceCreationLimitTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Dummy'
        )

    def test_space_creation_limit(self):
        # Create spaces up to the limit
        spaces = []
        for i in range(MAX_CREATED_SPACES_PER_USER):
            space = Space.objects.create(
                creator=self.user,
                name=f'Test Space {i+1}'
            )
            spaces.append(space)

        # Attempt to create one more space (should raise ValidationError)
        with self.assertRaises(ValidationError) as context:
            Space.objects.create(
                creator=self.user,
                name='One Space Too Many'
            )

        self.assertIn('creator', context.exception.message_dict)

    def test_space_editing_no_limit(self):
        # Create a space
        space = Space.objects.create(
            creator=self.user,
            name='Original Space Name'
        )

        # Should be able to edit the space even if user is at their limit
        # First, create remaining spaces up to the limit
        for i in range(MAX_CREATED_SPACES_PER_USER - 1):
            Space.objects.create(
                creator=self.user,
                name=f'Additional Space {i+1}'
            )

        # Now edit the original space (should not raise ValidationError)
        try:
            space.name = 'Updated Space Name'
            space.save()
        except ValidationError:
            self.fail("ValidationError was raised when editing an existing space")

        # Verify the change was saved
        updated_space = Space.objects.get(pk=space.pk)
        self.assertEqual(updated_space.name, 'Updated Space Name')


# ─── PendingInvite model ──────────────────────────────────────────────────────

class PendingInviteModelTests(TestCase):
    def setUp(self):
        self.admin = make_user('admin', 'admin@test.com')
        self.space = make_space(self.admin)

    def test_is_valid_fresh_invite(self):
        invite = PendingInvite.objects.create(
            email='new@test.com', space=self.space, invited_by=self.admin
        )
        self.assertTrue(invite.is_valid)

    def test_is_valid_accepted_invite(self):
        invite = PendingInvite.objects.create(
            email='new@test.com', space=self.space, invited_by=self.admin,
            accepted=True,
        )
        self.assertFalse(invite.is_valid)

    def test_is_valid_expired_invite(self):
        invite = PendingInvite.objects.create(
            email='new@test.com', space=self.space, invited_by=self.admin,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        self.assertFalse(invite.is_valid)

    def test_token_is_unique(self):
        a = PendingInvite.objects.create(email='a@test.com', space=self.space)
        b = PendingInvite.objects.create(email='b@test.com', space=self.space)
        self.assertNotEqual(a.token, b.token)


class CleanupExpiredInvitesCommandTests(TestCase):
    def setUp(self):
        self.admin = make_user('cleanup_admin', 'cleanup_admin@test.com')
        self.space = make_space(self.admin)

    def _invite(self, email, expired_days_ago=None, **extra):
        expires_at = (
            timezone.now() - timedelta(days=expired_days_ago)
            if expired_days_ago is not None
            else timezone.now() + timedelta(days=1)
        )
        return PendingInvite.objects.create(
            email=email, space=self.space, invited_by=self.admin,
            expires_at=expires_at, **extra,
        )

    def _run(self, *args):
        output = StringIO()
        call_command('cleanup_expired_invites', *args, stdout=output)
        return output.getvalue()

    def test_default_retention_deletes_only_invites_expired_over_30_days_ago(self):
        old = self._invite('old@test.com', expired_days_ago=31)
        recent = self._invite('recent@test.com', expired_days_ago=2)
        fresh = self._invite('fresh@test.com')

        out = self._run()

        self.assertFalse(PendingInvite.objects.filter(pk=old.pk).exists())
        self.assertTrue(PendingInvite.objects.filter(pk=recent.pk).exists())
        self.assertTrue(PendingInvite.objects.filter(pk=fresh.pk).exists())
        self.assertIn('Deleted 1 expired pending invite(s).', out)

    def test_accepted_invites_are_never_deleted(self):
        accepted = self._invite(
            'accepted@test.com', expired_days_ago=90,
            accepted=True, accepted_at=timezone.now() - timedelta(days=95),
        )

        self._run()
        self._run('--older-than-days', '0')

        self.assertTrue(PendingInvite.objects.filter(pk=accepted.pk).exists())

    def test_older_than_days_zero_deletes_everything_expired(self):
        just_expired = self._invite('just@test.com', expired_days_ago=0)
        fresh = self._invite('fresh@test.com')

        self._run('--older-than-days', '0')

        self.assertFalse(PendingInvite.objects.filter(pk=just_expired.pk).exists())
        self.assertTrue(PendingInvite.objects.filter(pk=fresh.pk).exists())

    def test_custom_retention_window(self):
        eight_days = self._invite('eight@test.com', expired_days_ago=8)
        three_days = self._invite('three@test.com', expired_days_ago=3)

        self._run('--older-than-days', '7')

        self.assertFalse(PendingInvite.objects.filter(pk=eight_days.pk).exists())
        self.assertTrue(PendingInvite.objects.filter(pk=three_days.pk).exists())

    def test_negative_retention_is_rejected(self):
        invite = self._invite('old@test.com', expired_days_ago=90)

        with self.assertRaises(CommandError):
            self._run('--older-than-days', '-1')

        self.assertTrue(PendingInvite.objects.filter(pk=invite.pk).exists())

    def test_dry_run_does_not_delete_invites(self):
        old = self._invite('dryrun@test.com', expired_days_ago=60)

        out = self._run('--dry-run')

        self.assertTrue(PendingInvite.objects.filter(pk=old.pk).exists())
        self.assertIn('Dry run: 1 expired pending invite(s) would be deleted.', out)

    def test_does_not_delete_spaces_or_roles(self):
        self._invite('old@test.com', expired_days_ago=60)

        self._run()

        self.assertTrue(Space.objects.filter(pk=self.space.pk).exists())
        self.assertTrue(SpaceRole.objects.filter(space=self.space, member=self.admin).exists())

    def test_logs_deleted_count(self):
        self._invite('old@test.com', expired_days_ago=60)

        with self.assertLogs('Models.spaces.management.commands.cleanup_expired_invites', level='INFO') as logs:
            self._run()

        self.assertIn('deleted 1 pending invite(s)', logs.output[0])

    def test_empty_table_is_a_noop(self):
        self.assertIn('Deleted 0 expired pending invite(s).', self._run())

    def test_expired_within_retention_still_reports_expired_via_api(self):
        """A recently expired invite survives cleanup, so the details endpoint says 'expired'."""
        recent = self._invite('recent@test.com', expired_days_ago=2)
        self._run()
        client = APIClient()
        client.force_authenticate(user=make_user('viewer', 'viewer@anon.firebase', anonymous=True))

        resp = client.get(reverse('invite-details'), {'token': str(recent.token)})

        self.assertEqual(resp.status_code, 400)
        self.assertIn('expired', resp.data['detail'])

    def test_purged_invite_returns_friendly_404_via_api(self):
        old = self._invite('old@test.com', expired_days_ago=60)
        token = str(old.token)
        self._run()
        client = APIClient()
        client.force_authenticate(user=make_user('viewer', 'viewer@anon.firebase', anonymous=True))

        resp = client.get(reverse('invite-details'), {'token': token})

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data['detail'], 'This invite link is invalid or has expired.')


# ─── SpaceRoleInviteApiView — new email path ──────────────────────────────────

class InviteNewEmailTests(TestCase):
    """
    When the invited email doesn't exist in the DB, the endpoint should create
    a PendingInvite and send the email via Resend (mocked).
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = make_user('admin', 'admin@test.com')
        self.space = make_space(self.admin)
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('spacerole-invite')

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_invite_unknown_email_creates_pending_invite(self, mock_send):
        resp = self.client.post(self.url, {
            'username_email': 'newperson@example.com',
            'role': 'member',
            'space': self.space.id,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(PendingInvite.objects.filter(email='newperson@example.com', space=self.space).exists())
        mock_send.assert_called_once()

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_invite_unknown_email_sends_correct_args(self, mock_send):
        self.client.post(self.url, {
            'username_email': 'newperson@example.com',
            'role': 'member',
            'space': self.space.id,
        })
        call_kwargs = mock_send.call_args.kwargs
        self.assertEqual(call_kwargs['to_email'], 'newperson@example.com')
        self.assertEqual(call_kwargs['space_name'], self.space.name)
        self.assertEqual(call_kwargs['invited_by_username'], self.admin.username)
        self.assertIn('invite=', call_kwargs['invite_link'])

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_reinviting_same_email_replaces_old_invite(self, mock_send):
        # First invite
        self.client.post(self.url, {
            'username_email': 'newperson@example.com',
            'role': 'member',
            'space': self.space.id,
        })
        first_token = PendingInvite.objects.get(email='newperson@example.com').token

        # Re-invite — should delete the old one and create a fresh token
        self.client.post(self.url, {
            'username_email': 'newperson@example.com',
            'role': 'member',
            'space': self.space.id,
        })
        invites = PendingInvite.objects.filter(email='newperson@example.com', space=self.space)
        self.assertEqual(invites.count(), 1)
        self.assertNotEqual(invites.first().token, first_token)

    @patch('Models.spaces.api.api.send_space_invite_email', side_effect=Exception('Resend down'))
    def test_email_failure_cleans_up_invite(self, mock_send):
        resp = self.client.post(self.url, {
            'username_email': 'newperson@example.com',
            'role': 'member',
            'space': self.space.id,
        })
        self.assertEqual(resp.status_code, 500)
        # Invite must not persist when email delivery fails
        self.assertFalse(PendingInvite.objects.filter(email='newperson@example.com').exists())

    @patch('Models.spaces.api.api.send_space_invite_email')
    def test_invite_existing_user_uses_normal_path(self, mock_send):
        existing = make_user('existing', 'existing@test.com')
        resp = self.client.post(self.url, {
            'username_email': 'existing@test.com',
            'role': 'member',
            'space': self.space.id,
        })
        # Normal path → 201 Created, no PendingInvite, no email
        self.assertEqual(resp.status_code, 201)
        self.assertFalse(PendingInvite.objects.filter(email='existing@test.com').exists())
        mock_send.assert_not_called()


# ─── InviteDetailsApiView ─────────────────────────────────────────────────────

class InviteDetailsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.anon = make_user('anon', 'anon@anon.firebase', anonymous=True)
        self.client.force_authenticate(user=self.anon)
        self.admin = make_user('admin2', 'admin2@test.com')
        self.space = make_space(self.admin)
        self.invite = PendingInvite.objects.create(
            email='invited@test.com', space=self.space, invited_by=self.admin
        )
        self.url = reverse('invite-details')

    def test_valid_token_returns_space_name_and_masked_email(self):
        resp = self.client.get(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['space_name'], self.space.name)
        # Email starts with 'in', so masked form is 'in***@test.com'
        self.assertEqual(resp.data['masked_email'], 'in***@test.com')

    def test_missing_token_returns_400(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 400)

    def test_unknown_token_returns_404(self):
        resp = self.client.get(self.url, {'token': 'aaaaaaaa-0000-0000-0000-000000000000'})
        self.assertEqual(resp.status_code, 404)

    def test_expired_token_returns_400(self):
        self.invite.expires_at = timezone.now() - timedelta(hours=1)
        self.invite.save()
        resp = self.client.get(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 400)

    def test_already_accepted_returns_400(self):
        self.invite.accepted = True
        self.invite.save()
        resp = self.client.get(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 400)


# ─── InviteAcceptApiView ──────────────────────────────────────────────────────

class InviteAcceptTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_user('admin3', 'admin3@test.com')
        self.space = make_space(self.admin)
        self.invite = PendingInvite.objects.create(
            email='joiner@test.com', space=self.space, invited_by=self.admin
        )
        self.url = reverse('invite-accept')

    def _joiner(self, email: str = 'joiner@test.com') -> User:
        return make_user('joiner', email)

    def test_happy_path_creates_spacerole(self):
        joiner = self._joiner()
        self.client.force_authenticate(user=joiner)
        resp = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(SpaceRole.objects.filter(member=joiner, space=self.space).exists())

    def test_happy_path_marks_invite_accepted(self):
        joiner = self._joiner()
        self.client.force_authenticate(user=joiner)
        self.client.post(self.url, {'token': str(self.invite.token)})
        self.invite.refresh_from_db()
        self.assertTrue(self.invite.accepted)
        self.assertIsNotNone(self.invite.accepted_at)

    def test_anonymous_user_is_rejected(self):
        anon = make_user('anon2', 'anon2@anon.firebase', anonymous=True)
        self.client.force_authenticate(user=anon)
        resp = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 403)

    def test_expired_invite_is_rejected(self):
        self.invite.expires_at = timezone.now() - timedelta(hours=1)
        self.invite.save()
        joiner = self._joiner()
        self.client.force_authenticate(user=joiner)
        resp = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 400)

    def test_already_accepted_invite_is_rejected(self):
        self.invite.accepted = True
        self.invite.accepted_at = timezone.now()
        self.invite.save()
        joiner = self._joiner()
        self.client.force_authenticate(user=joiner)
        resp = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 400)

    def test_wrong_email_is_rejected(self):
        wrong_user = make_user('wrongperson', 'wrong@test.com')
        self.client.force_authenticate(user=wrong_user)
        resp = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 403)

    def test_email_comparison_is_case_insensitive(self):
        # User email has different casing than the invite email
        joiner = make_user('joiner_caps', 'JOINER@TEST.COM')
        self.client.force_authenticate(user=joiner)
        resp = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp.status_code, 201)

    def test_missing_token_returns_400(self):
        joiner = self._joiner()
        self.client.force_authenticate(user=joiner)
        resp = self.client.post(self.url, {})
        self.assertEqual(resp.status_code, 400)

    def test_double_accept_is_idempotent_not_duplicate(self):
        """A second accept call on the same token must not create a second SpaceRole."""
        joiner = self._joiner()
        self.client.force_authenticate(user=joiner)
        self.client.post(self.url, {'token': str(self.invite.token)})
        resp2 = self.client.post(self.url, {'token': str(self.invite.token)})
        self.assertEqual(resp2.status_code, 400)
        self.assertEqual(SpaceRole.objects.filter(member=joiner, space=self.space).count(), 1)

