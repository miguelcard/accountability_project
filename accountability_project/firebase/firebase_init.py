"""
Firebase Admin SDK initialization.

Initializes the Firebase Admin SDK exactly once when imported.
The SDK is configured using either:
  1. GOOGLE_APPLICATION_CREDENTIALS env var (path to service account JSON), or
  2. FIREBASE_CREDENTIALS_JSON env var (inline JSON string — useful in containers), or
  3. Application Default Credentials (e.g. when running on GCP).
"""

import os
import json
import logging

import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)


def initialize_firebase():
    """Initialize the Firebase Admin SDK if it hasn't been initialized yet."""
    if firebase_admin._apps:
        # Already initialised — nothing to do.
        return

    cred = None

    # Option 1: Inline JSON string (handy for Docker / CI) (not used for now)
    json_str = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if json_str:
        cred = credentials.Certificate(json.loads(json_str))
        logger.info("Firebase Admin SDK initialised from FIREBASE_CREDENTIALS_JSON env var.")

    # Option 2: Path to a service-account key file
    if cred is None:
        key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if key_path:
            cred = credentials.Certificate(key_path)
            logger.info("Firebase Admin SDK initialised from GOOGLE_APPLICATION_CREDENTIALS (%s).", key_path)

    if cred is None:
        raise RuntimeError(
            "Firebase credentials not found. Set either GOOGLE_APPLICATION_CREDENTIALS "
            "(path to service-account JSON) or FIREBASE_CREDENTIALS_JSON (inline JSON string)."
        )

    firebase_admin.initialize_app(cred)
