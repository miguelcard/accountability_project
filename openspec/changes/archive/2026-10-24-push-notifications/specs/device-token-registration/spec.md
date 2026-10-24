## ADDED Requirements

### Requirement: Register a device token
The system SHALL allow an authenticated user to register an FCM device token via `POST /v1/devices/` with `token` and `platform` (`android` or `ios`).

#### Scenario: New token
- **WHEN** an authenticated user posts a token not yet stored
- **THEN** a `DeviceToken` is created for that user and the response is 200/201

#### Scenario: Existing token, same user
- **WHEN** the same user posts an already registered token
- **THEN** no duplicate is created and `last_seen` is updated

#### Scenario: Existing token, different user
- **WHEN** another authenticated user posts a token owned by a different user
- **THEN** the token is re-assigned to the requesting user

#### Scenario: Unauthenticated
- **WHEN** the request has no valid credentials
- **THEN** the system responds 401 and stores nothing

#### Scenario: Invalid input
- **WHEN** `token` is empty or `platform` is not allowed
- **THEN** the system responds 400

### Requirement: Unregister a device token
The system SHALL allow an authenticated user to remove their own token via `DELETE /v1/devices/`.

#### Scenario: Own token
- **WHEN** a user deletes a token they own
- **THEN** it is removed and the response is 204

#### Scenario: Token owned by someone else or unknown
- **WHEN** a user deletes a token they do not own
- **THEN** nothing is deleted and the response is 204 (no information leak)
