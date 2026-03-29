"""
Firebase App Check verification middleware.

Reads the ``X-Firebase-AppCheck`` header from incoming requests and verifies
it using the Firebase Admin SDK.  The result is annotated on the request so
views / permission classes can inspect ``request.app_check_verified``.

Behaviour is controlled by the ``FIREBASE_APP_CHECK_ENFORCEMENT`` setting:

    "monitoring"   (default) — logs warnings for missing / invalid tokens but
                               allows the request through.  Use during rollout.
    "enforced"     — rejects requests without a valid App Check token with 403.

Usage — add to MIDDLEWARE in settings.py:

    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        ...
        'firebase.app_check_middleware.FirebaseAppCheckMiddleware',
        ...
    ]
"""

import logging

from django.conf import settings
from django.http import JsonResponse
from firebase_admin import app_check

logger = logging.getLogger(__name__)


class FirebaseAppCheckMiddleware:
    """Django middleware that verifies Firebase App Check tokens."""

    def __init__(self, get_response):
        self.get_response = get_response
        # Read enforcement mode once at startup
        self.enforcement = getattr(settings, "FIREBASE_APP_CHECK_ENFORCEMENT", "monitoring")
        logger.info(
            "FirebaseAppCheckMiddleware initialised in '%s' mode.",
            self.enforcement,
        )

    def __call__(self, request):
        # --- Skip non-API paths (admin, docs, schema, static, etc.) ---
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        app_check_token = request.META.get("HTTP_X_FIREBASE_APPCHECK")

        if not app_check_token:
            request.app_check_verified = False
            if self.enforcement == "enforced":
                logger.warning(
                    "App Check ENFORCED — missing token. path=%s ip=%s",
                    request.path,
                    self._get_client_ip(request),
                )
                return JsonResponse(
                    {"detail": "Missing Firebase App Check token."},
                    status=403,
                )
            else:
                logger.info(
                    "App Check MONITORING — missing token. path=%s ip=%s",
                    request.path,
                    self._get_client_ip(request),
                )
                return self.get_response(request)

        # --- Verify the token ---
        try:
            claims = app_check.verify_token(app_check_token)
            request.app_check_verified = True
            request.app_check_claims = claims
            logger.debug(
                "App Check token verified. path=%s app_id=%s",
                request.path,
                claims.get("sub", "unknown"),
            )
        except Exception as exc:
            request.app_check_verified = False
            if self.enforcement == "enforced":
                logger.warning(
                    "App Check ENFORCED — invalid token. path=%s ip=%s error=%s",
                    request.path,
                    self._get_client_ip(request),
                    exc,
                )
                return JsonResponse(
                    {"detail": "Invalid Firebase App Check token."},
                    status=403,
                )
            else:
                logger.warning(
                    "App Check MONITORING — invalid token (allowing through). path=%s ip=%s error=%s",
                    request.path,
                    self._get_client_ip(request),
                    exc,
                )

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request) -> str:
        """Extract client IP, respecting X-Forwarded-For from reverse proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
