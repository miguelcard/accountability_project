# push-notification-delivery Specification

## Purpose
TBD - created by archiving change push-notifications. Update Purpose after archive.
## Requirements
### Requirement: Deliver push to all of a user's devices
The system SHALL provide `notify_user(recipient, title, body, data)` that sends a push via FCM to every `DeviceToken` of the recipient.

#### Scenario: Multiple devices
- **WHEN** the recipient has two registered tokens
- **THEN** one message is sent per token

#### Scenario: No tokens
- **WHEN** the recipient has no tokens
- **THEN** nothing is sent and no error is raised

### Requirement: Handle delivery failures safely
The system MUST NOT fail the calling request when delivery fails, and SHALL remove tokens that FCM reports as invalid or unregistered.

#### Scenario: Unregistered token
- **WHEN** FCM reports a token as unregistered
- **THEN** that `DeviceToken` is deleted

#### Scenario: FCM outage
- **WHEN** the FCM call raises an error
- **THEN** the error is logged and the original API response is unaffected

### Requirement: Notify a user when added to a space
The system SHALL send a push to an existing user when another user creates a `SpaceRole` for them, after the transaction commits.

#### Scenario: Added by another user
- **WHEN** user A adds existing user B to a space
- **THEN** B receives a push stating they were added to that space

#### Scenario: Self action
- **WHEN** the actor and recipient are the same user
- **THEN** no push is sent

#### Scenario: Rollback
- **WHEN** the transaction creating the `SpaceRole` is rolled back
- **THEN** no push is sent

#### Scenario: Privacy
- **WHEN** the push is composed
- **THEN** it contains only the actor username and space name

