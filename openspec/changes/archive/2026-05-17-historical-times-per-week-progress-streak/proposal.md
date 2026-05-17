## Why

When a user changes a habit's `times` (target completions per week or month), the streak badge returned by the API immediately re-evaluates all past periods against the new target — retroactively inflating or deflating streaks. The `RecurrentHabitConfigHistory` table already records every target change with its `effective_from` date, and `_config_for_period()` already resolves the correct historical target for XP calculation, but `_compute_streak()` in the serializer still uses the live `habit.times` value for every past period.

## What Changes

- `_compute_streak()` in `accountability_project/Models/habits/api/serializers.py` is updated to call `_config_for_period(habit, period_start)` for each period walked backwards, so every past period is evaluated against the target that was actually in effect that week/month.
- `RecurrentHabitSerializerToRead` gains a new read-only field `config_history` — a lightweight list of `{ effective_from, times, time_frame }` entries sorted ascending by `effective_from` — consumed by the frontend to resolve the historically-correct `times` for the progress bar denominator.
- Prefetch of `config_history` added to all API views that serve habits (`AllHabitsApiView`, `SpaceHabitsApiView`, `RecurrentHabitApiView`) to avoid N+1 queries.

## Capabilities

### New Capabilities

- `habit-config-history-api`: The habit API response exposes a `config_history` array so consumers can resolve the historically-correct `times`/`time_frame` for any past date without additional requests.

### Modified Capabilities

_(none — no existing backend specs)_

## Impact

- `accountability_project/Models/habits/api/serializers.py` — `_compute_streak()` updated; `config_history` field added to `RecurrentHabitSerializerToRead`.
- `accountability_project/Models/habits/api/api.py` — `prefetch_related('config_history')` added to relevant views.
- `accountability_project/Models/habits/xp_utils.py` — `_config_for_period()` reused (no changes to this function).
- API response shape change: `config_history` array added to every habit object (additive, non-breaking).
- Frontend companion change required to consume `config_history` for progress bar denominator.
