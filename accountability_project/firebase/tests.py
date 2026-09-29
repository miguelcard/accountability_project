from django.test import TestCase

from Models.users.models import User
from firebase.authentication import FirebaseAuthentication


def make_decoded_token(uid: str, sign_in_provider: str, email: str = "") -> dict:
    """Builds a minimal Firebase decoded-token dict, shaped like what
    firebase_admin.auth.verify_id_token() returns."""
    return {
        "uid": uid,
        "email": email,
        "firebase": {"sign_in_provider": sign_in_provider},
    }


class GetOrCreateUserTests(TestCase):
    """
    Covers FirebaseAuthentication._get_or_create_user(), in particular the
    anonymous -> registered upgrade sync that happens after linkWithCredential()
    (frontend) results in the *same* firebase_uid being re-sent with a
    non-anonymous sign_in_provider.
    """

    def test_creates_new_anonymous_user(self):
        token = make_decoded_token("uid_new_anon", "anonymous")
        user = FirebaseAuthentication._get_or_create_user(token)

        self.assertEqual(user.firebase_uid, "uid_new_anon")
        self.assertTrue(user.is_anonymous_firebase_user)
        self.assertEqual(User.objects.filter(firebase_uid="uid_new_anon").count(), 1)

    def test_creates_new_non_anonymous_user(self):
        token = make_decoded_token("uid_new_named", "password", email="named@test.com")
        user = FirebaseAuthentication._get_or_create_user(token)

        self.assertFalse(user.is_anonymous_firebase_user)
        self.assertEqual(user.email, "named@test.com")

    def test_returning_anonymous_user_is_unchanged(self):
        # First sighting creates the anonymous user.
        token = make_decoded_token("uid_still_anon", "anonymous")
        FirebaseAuthentication._get_or_create_user(token)

        # Second request with the same anonymous token should not alter the user.
        user = FirebaseAuthentication._get_or_create_user(token)

        self.assertTrue(user.is_anonymous_firebase_user)
        self.assertEqual(user.email, "uid_still_anon@anonymous.firebase")

    def test_anonymous_user_upgrades_to_email_account_after_link(self):
        """
        Simulates the real invite flow:
        1. User signs in anonymously (uid X, sign_in_provider="anonymous").
        2. User calls linkWithEmail() on the frontend, which upgrades the SAME
           Firebase uid X to sign_in_provider="password" with a real email.
        3. The next authenticated request carries a decoded token for uid X with
           the new provider/email -> the Django User row must be upgraded in place
           (same PK, no duplicate row), so PendingInvite email-matching succeeds.
        """
        uid = "uid_link_flow"

        pre_link_token = make_decoded_token(uid, "anonymous")
        anon_user = FirebaseAuthentication._get_or_create_user(pre_link_token)
        self.assertTrue(anon_user.is_anonymous_firebase_user)
        original_pk = anon_user.pk

        post_link_token = make_decoded_token(uid, "password", email="upgraded@test.com")
        upgraded_user = FirebaseAuthentication._get_or_create_user(post_link_token)

        self.assertEqual(upgraded_user.pk, original_pk, "must upgrade the same row, not create a new one")
        self.assertFalse(upgraded_user.is_anonymous_firebase_user)
        self.assertEqual(upgraded_user.email, "upgraded@test.com")
        self.assertEqual(User.objects.filter(firebase_uid=uid).count(), 1)

    def test_upgrade_conflict_when_email_already_taken_keeps_user_anonymous(self):
        """
        If another Django user already owns the target email (e.g. a stale/duplicate
        registration), the upgrade must not crash and must leave the anonymous user
        as-is rather than raising an unhandled IntegrityError.
        """
        User.objects.create(
            username="existing_owner",
            email="taken@test.com",
            firebase_uid="uid_existing_owner",
        )

        uid = "uid_conflict"
        pre_link_token = make_decoded_token(uid, "anonymous")
        anon_user = FirebaseAuthentication._get_or_create_user(pre_link_token)
        self.assertTrue(anon_user.is_anonymous_firebase_user)

        post_link_token = make_decoded_token(uid, "password", email="taken@test.com")
        result_user = FirebaseAuthentication._get_or_create_user(post_link_token)

        result_user.refresh_from_db()
        self.assertTrue(result_user.is_anonymous_firebase_user)
        self.assertNotEqual(result_user.email, "taken@test.com")
