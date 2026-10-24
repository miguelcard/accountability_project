## Why

Users have no way of knowing they were added to a space unless they open the app. Modern social apps deliver OS-level push notifications even when the app is closed. The backend has no device registry and no FCM sender today.

## What Changes

- New Django app `Models/notifications` with a `DeviceToken` model.
- Endpoints to register and unregister a device token for the authenticated user.
- A sender service `notify_user()` that delivers push via Firebase Cloud Messaging (`firebase_admin.messaging`) and prunes invalid tokens.
- First event: an existing user receives a push when a `SpaceRole` is created for them by someone else.
- No in-app inbox, no read state, no preferences in this change (deferred).

## Capabilities

### New Capabilities
- `device-token-registration`: register, refresh and unregister push device tokens per user.
- `push-notification-delivery`: send push to all of a user's devices, handle FCM errors, and trigger on space-added.

### Modified Capabilities

## Impact

- New app `Models/notifications` (models, migration, api, services, tests); registered in `INSTALLED_APPS` and `urls.py`.
- `Models/spaces/api/api.py` (existing-user invite path) calls `notify_user` on commit.
- Reuses existing Firebase Admin initialization (`firebase/firebase_init.py`); no new dependency expected beyond `firebase_admin`.
- Cross-repo contract with `acc-frontend-nextjs` change `push-notifications`.
