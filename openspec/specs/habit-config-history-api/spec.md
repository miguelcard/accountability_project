# habit-config-history-api Specification

## Purpose
TBD - created by archiving change historical-times-per-week-progress-streak. Update Purpose after archive.
## Requirements
### Requirement: config_history field in habit API response
The habit API response (for all endpoints that return `RecurrentHabit` objects, including `/api/habits/`, `/api/spaces/<id>/`, and `/api/habits/<id>/`) SHALL include a `config_history` field on each habit object.

`config_history` SHALL be a list of objects sorted ascending by `effective_from`, each containing:
- `effective_from` (ISO 8601 date string): the date from which this configuration became active
- `times` (integer): the completions-per-period target active from this date
- `time_frame` (string `"W"` or `"M"`): the period type active from this date

The list SHALL include all `RecurrentHabitConfigHistory` rows for the habit. It SHALL NOT be paginated. It MAY be an empty list if no history rows exist (pre-feature data).

The field SHALL be populated using a prefetched queryset to avoid N+1 database queries.

#### Scenario: Habit with multiple config changes
- **WHEN** a habit has been changed from `times=3` to `times=1` on a specific date
- **THEN** `config_history` SHALL contain at least two entries: one for the original config and one for the update, sorted by `effective_from` ascending

#### Scenario: Habit with no config history
- **WHEN** a habit has no `RecurrentHabitConfigHistory` rows
- **THEN** `config_history` SHALL be an empty list `[]`

#### Scenario: config_history included in space habits response
- **WHEN** a client fetches a space's details including its habits
- **THEN** each habit in the response SHALL include a `config_history` field following the above format

#### Scenario: config_history included in single habit response
- **WHEN** a client fetches a single habit by ID
- **THEN** the response SHALL include a `config_history` field following the above format

### Requirement: Streak computed against historical targets
The `streak` field returned on each habit object SHALL reflect the number of consecutive past periods in which the user met their habit goal as measured against the target (`times`) that was in effect during each respective period.

The backend SHALL use `RecurrentHabitConfigHistory` to resolve the correct `(times, time_frame)` for each period walked during streak computation, identically to how `_config_for_period` is used in XP calculation.

A change to the current `times` value MUST NOT alter the streak count for any period that was already evaluated under a different target.

#### Scenario: Target increased after under-performing weeks
- **WHEN** a habit had `times=3`, the user completed it 1×/week for 2 weeks, and then changed `times` to `1`
- **THEN** the returned `streak.count` SHALL be `0` (those weeks did not meet the goal of 3 in effect at the time)

#### Scenario: Target decreased after fully-meeting weeks
- **WHEN** a habit had `times=1`, the user completed it 1×/week for 3 consecutive weeks, and then changed `times` to `3`
- **THEN** the returned `streak.count` SHALL be `3` (those weeks met the goal of 1 in effect at the time)

#### Scenario: Streak unaffected for periods before any config change
- **WHEN** a habit has never had its target changed and the user has met the goal for 5 consecutive weeks
- **THEN** the returned `streak.count` SHALL be `5`

