## Why

When a user changes a habit's `time_frame` (e.g. Weekly → Monthly), the new config currently takes effect immediately (`effective_from = today`). This creates a dead zone of up to ~3.5 weeks where no XP can be earned — the old weekly rule has ended but the new monthly period won't close until the 1st of next month. Users are silently penalised with no explanation and no recourse.

## What Changes

- **`effective_from` deferred for time_frame changes**: When `time_frame` changes (W→M or M→W), `effective_from` is set to the **start of the next full period** under the new `time_frame`, not today. For W→M this means the 1st of the following month; for M→W this means the next Monday. The old rule continues earning XP through the remainder of the current period — eliminating the dead zone.
- **`config_transition` field added to PATCH response**: When a PATCH changes `time_frame`, the response includes a `config_transition` object containing `old_time_frame`, `new_time_frame`, and `new_effective_from` (ISO date string). The frontend uses this to show the user exactly when the new rule kicks in.
- **`habit-config-change-api` spec updated**: The existing spec for how config changes are persisted now reflects the deferred `effective_from` logic for time_frame transitions and the new response field.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `habit-config-history-api`: The requirement for how `effective_from` is set on a `RecurrentHabitConfigHistory` row when `time_frame` changes — now deferred to the next clean period boundary rather than today. Also adds the `config_transition` response contract.

## Impact

- `accountability_project/Models/habits/api/serializers.py` — `RecurrentHabitSerializerToWrite.update()`: change `effective_from` calculation for time_frame transitions; add `config_transition` to `to_representation()` output (or return from `update()` via response context).
- `accountability_project/Models/habits/tests.py` — serializer integration tests must be updated/added to cover the deferred effective_from behaviour for both W→M and M→W.
- No model migrations required. No breaking changes to existing API consumers (field is additive).
