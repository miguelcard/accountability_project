## ADDED Requirements

### Requirement: effective_from set to next clean period boundary for time_frame changes
When a `RecurrentHabit`'s `time_frame` is changed, the system SHALL write a new `RecurrentHabitConfigHistory` row with `effective_from` set to the **first day of the next full period under the new `time_frame`**, not today.

The formula SHALL be:
- **W → M**: `effective_from` = the 1st of the following month (e.g. changing on any day in May → June 1)
- **M → W**: `effective_from` = the Monday of the following week (e.g. changing on May 23 → May 25)

If today is already the first day of the new period (e.g. W→M on June 1, or M→W on a Monday), the system SHALL defer by one additional full period (e.g. W→M on June 1 → July 1; M→W on Monday May 25 → Monday June 1).

The old config rule SHALL continue to govern XP evaluation for all periods between today and `effective_from`. The existing `settle_habit_xp_before_config_change` call MUST still be made before saving the new config row.

Changes where only `times` changes (no `time_frame` change) SHALL continue to backdate `effective_from` to the start of the current period (existing behaviour, unchanged).

#### Scenario: W→M change mid-month eliminates dead zone
- **WHEN** a user changes a weekly habit to monthly on May 23
- **THEN** a `RecurrentHabitConfigHistory` row SHALL be written with `effective_from = 2026-06-01`
- **AND** the week of May 25–31 SHALL still be evaluatable as a weekly XP period under the old config

#### Scenario: W→M change on first day of month defers a full extra month
- **WHEN** a user changes a weekly habit to monthly on June 1
- **THEN** a `RecurrentHabitConfigHistory` row SHALL be written with `effective_from = 2026-07-01`
- **AND** all weeks in June SHALL still be evaluatable as weekly XP periods under the old config

#### Scenario: M→W change defers to next Monday
- **WHEN** a user changes a monthly habit to weekly on May 23 (a Saturday)
- **THEN** a `RecurrentHabitConfigHistory` row SHALL be written with `effective_from = 2026-05-25` (the following Monday)
- **AND** the month of May SHALL still be evaluatable as a monthly XP period under the old config when May closes

#### Scenario: M→W change on a Monday defers by one full week
- **WHEN** a user changes a monthly habit to weekly on Monday May 25
- **THEN** a `RecurrentHabitConfigHistory` row SHALL be written with `effective_from = 2026-06-01` (the following Monday)

#### Scenario: times-only change behaviour is unchanged
- **WHEN** a user changes `times` from 3 to 1 without changing `time_frame`
- **THEN** `effective_from` SHALL be set to the start of the current period (Monday of current week for W, 1st of current month for M), unchanged from existing behaviour

### Requirement: config_transition field in time_frame change PATCH response
When a PATCH request to a `RecurrentHabit` endpoint results in a `time_frame` change, the response SHALL include a top-level `config_transition` object alongside the serialized habit data.

`config_transition` SHALL contain:
- `old_time_frame` (string `"W"` or `"M"`): the time_frame before the change
- `new_time_frame` (string `"W"` or `"M"`): the time_frame after the change
- `new_effective_from` (ISO 8601 date string): the date the new config takes effect (matching the `effective_from` written to `RecurrentHabitConfigHistory`)

The field SHALL be **absent** (not `null`) when the PATCH does not change `time_frame`.

#### Scenario: W→M PATCH response includes config_transition
- **WHEN** a PATCH request changes a habit's `time_frame` from `"W"` to `"M"` on May 23
- **THEN** the response SHALL include `"config_transition": {"old_time_frame": "W", "new_time_frame": "M", "new_effective_from": "2026-06-01"}`

#### Scenario: M→W PATCH response includes config_transition
- **WHEN** a PATCH request changes a habit's `time_frame` from `"M"` to `"W"` on May 23
- **THEN** the response SHALL include `"config_transition": {"old_time_frame": "M", "new_time_frame": "W", "new_effective_from": "2026-05-25"}`

#### Scenario: PATCH with no time_frame change omits config_transition
- **WHEN** a PATCH request changes only `times` (not `time_frame`)
- **THEN** the response SHALL NOT include a `config_transition` field

#### Scenario: PATCH with no config change omits config_transition
- **WHEN** a PATCH request changes only `description` or `title`
- **THEN** the response SHALL NOT include a `config_transition` field
