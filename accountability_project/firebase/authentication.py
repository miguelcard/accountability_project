"""
DRF authentication backend that verifies Firebase ID tokens.

Usage — set as a DEFAULT_AUTHENTICATION_CLASSES entry in settings.py:

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'firebase.authentication.FirebaseAuthentication',
        ],
        ...
    }

Every incoming request with an ``Authorization: Bearer <firebase_id_token>``
header will be verified against Firebase.  If the token is valid the
corresponding Django ``User`` is returned (auto-created on first sight).
"""

import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from firebase_admin import auth as firebase_auth
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from Models.users.models import User

logger = logging.getLogger(__name__)


class FirebaseAuthentication(BaseAuthentication):
    """Authenticate requests using a Firebase ID token (Bearer token)."""

    keyword = "Bearer"

    # ------------------------------------------------------------------ #
    #  Main entry-point called by DRF on every request
    # ------------------------------------------------------------------ #
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None  # No credentials provided — let other backends try or deny.

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            return None  # Not a Bearer token — skip.

        id_token = parts[1]

        # ---------- verify the Firebase token ---------- #
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except firebase_auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed("Firebase token has expired.")
        except firebase_auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed("Firebase token has been revoked.")
        except firebase_auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed("Invalid Firebase token.")
        except Exception as exc:
            logger.exception("Unexpected error verifying Firebase token")
            raise exceptions.AuthenticationFailed(f"Firebase token verification failed: {exc}")

        firebase_uid = decoded_token.get("uid")
        if not firebase_uid:
            raise exceptions.AuthenticationFailed("Firebase token missing uid claim.")

        # ---------- look up or auto-create the Django user ---------- #
        user = self._get_or_create_user(decoded_token)

        # Return (user, auth_info) — DRF stores auth_info in request.auth
        return (user, decoded_token)

    # ------------------------------------------------------------------ #
    #  User resolution
    # ------------------------------------------------------------------ #
    @staticmethod
    def _get_or_create_user(decoded_token: dict) -> User:
        """
        Find an existing user by ``firebase_uid``, or create one with
        sensible defaults for an anonymous Firebase user.
        """
        firebase_uid: str = decoded_token["uid"]

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            # If this was an anonymous user who has since linked an email/password account,
            # sync the new email and clear the anonymous flag so the Django user reflects
            # the upgrade transparently on the very next request.
            if user.is_anonymous_firebase_user:
                sign_in_provider = decoded_token.get("firebase", {}).get("sign_in_provider", "")
                new_email = decoded_token.get("email", "")
                if sign_in_provider != "anonymous" and new_email:
                    user.email = new_email
                    user.is_anonymous_firebase_user = False
                    try:
                        # Wrapped in its own savepoint so an IntegrityError (email already
                        # taken) only rolls back this save, not any outer transaction the
                        # caller might be running in (e.g. if ATOMIC_REQUESTS is ever enabled).
                        with transaction.atomic():
                            user.save(update_fields=["email", "is_anonymous_firebase_user", "updated_at"])
                        logger.info(
                            "Upgraded anonymous user id=%s to email account (email=%s)",
                            user.pk,
                            new_email,
                        )
                    except IntegrityError:
                        # Another Django user already owns this email (e.g. a previous
                        # registration). Revert the in-memory changes so the returned
                        # object reflects the real (unchanged) DB state, log, and continue —
                        # the user stays anonymous on the Django side until the conflict is resolved.
                        user.email = User.objects.get(pk=user.pk).email
                        user.is_anonymous_firebase_user = True
                        logger.warning(
                            "Could not upgrade anonymous user id=%s to email=%s: "
                            "email already belongs to another account.",
                            user.pk,
                            new_email,
                        )
            return user
        except User.DoesNotExist:
            pass

        # Auto-create a new user for this Firebase UID.
        # Anonymous users have no email — generate a placeholder username
        # so the unique constraint is satisfied.
        email = decoded_token.get("email", "")
        is_anonymous = decoded_token.get("firebase", {}).get("sign_in_provider") == "anonymous"

        username = f"fb_{firebase_uid[:20]}"  # deterministic, unique-enough

        user = User(
            firebase_uid=firebase_uid,
            username=username,
            email=email or f"{firebase_uid}@anonymous.firebase",
            is_anonymous_firebase_user=is_anonymous,
        )

        # No usable password — these users authenticate via Firebase.
        user.set_unusable_password()
        user.save()

        logger.info(
            "Auto-created user id=%s for firebase_uid=%s (anonymous=%s)",
            user.pk,
            firebase_uid,
            is_anonymous,
        )
        return user
