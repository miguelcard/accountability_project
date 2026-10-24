## Context

The backend is Django/DRF with Firebase authentication (`firebase/authentication.py`) and Firebase Admin initialised in `firebase/firebase_init.py`. There is no Celery; emails are sent synchronously. For an existing user, `SpaceRoleInviteApiView` delegates to `SpaceRoleSerializer`, which creates a `SpaceRole` immediately (no pending state).

## Goals / Non-Goals

**Goals:**
- Persist device tokens per user and push to all of them via FCM.
- Trigger a push when a user is added to a space by someone else.
- Make adding future event types a one-call change.

**Non-Goals:**
- In-app inbox, read state, preferences, deep links, email changes.
- Background queue (Celery), websockets.
- Changing the invite flow (e.g. Accept/Decline).

## Decisions

- **New app `Models/notifications`**, mirroring `users`, `spaces` and `habits`. Keeps the concern isolated.
- **`DeviceToken(user FK CASCADE, token unique, platform, created_at, last_seen)`.** Token is globally unique; registering an existing token re-assigns it to the current user (covers logout/login of a different user on one device).
- **Endpoints:** `POST /v1/devices/` (upsert) and `DELETE /v1/devices/` (body: token; only deletes the caller's own token). Authenticated and rate limited like other endpoints.
- **`notify_user(recipient, title, body, data=None)`** in `notifications/services.py` is the single delivery entry point. It sends one FCM message per token and deletes tokens on `UNREGISTERED`/`INVALID_ARGUMENT`. All exceptions are caught and logged so they never fail the calling request. Alternative considered: Django signals (rejected: hidden flow, hard to test).
- **Synchronous send, invoked via `transaction.on_commit`.** Avoids phantom pushes on rollback. Alternative: Celery (rejected as over-engineering for v1). Upgrade path: wrap `notify_user` in a task later.
- **Minimal payload text** (e.g. "You were added to <space>") since it shows on the lock screen. No private data.
- **Skip self-notifications** (actor == recipient) and anonymous users without tokens.

## Risks / Trade-offs

- [Synchronous FCM call adds request latency] → short timeout, send after commit, move to a queue if it becomes an issue.
- [Stale tokens accumulate] → prune on FCM error responses.
- [Token shared across users on one device] → upsert re-assigns ownership.
- [Service account lacks FCM permission] → verify in the first Android end-to-end test.
