## 1. Device tokens

- [x] 1.1 Create `Models/notifications` app (apps.py, registered in `INSTALLED_APPS`)
- [x] 1.2 Add `DeviceToken` model and migration
- [x] 1.3 Add serializer and `POST /v1/devices/` upsert view with rate limit
- [x] 1.4 Add `DELETE /v1/devices/` (own tokens only) and wire URLs in `urls.py`
- [x] 1.5 Tests for register, re-assign, unregister, auth and validation

## 2. FCM sender

- [x] 2.1 Implement `notify_user()` in `notifications/services.py` using `firebase_admin.messaging`
- [x] 2.2 Prune tokens on unregistered/invalid FCM errors; catch and log all other errors
- [x] 2.3 Tests with FCM mocked (multi-device, no tokens, pruning, outage)

## 3. First event

- [x] 3.1 Call `notify_user` via `transaction.on_commit` after `SpaceRole` creation for an existing user
- [x] 3.2 Skip self-notifications
- [x] 3.3 Tests for added, self action and rollback

## 4. Verification

- [x] 4.1 Confirm the service account can send FCM messages
- [x] 4.2 End-to-end check with the Android app closed (coordinated with frontend change)
