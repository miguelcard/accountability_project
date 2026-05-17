## 1. Fix streak calculation to use historical targets

- [x] 1.1 In `accountability_project/Models/habits/api/serializers.py`, update `_compute_streak()` to use the prefetched `config_history` related manager on each period iteration instead of `habit.times` / `habit.time_frame`. For each backward step, find the latest `config_history` entry where `effective_from` ≤ `period_start` to get `(required, time_frame)` for that period. Fall back to `habit.times` / `habit.time_frame` if no matching entry exists.
- [x] 1.2 Verify that `_compute_streak()` no longer references `habit.times` or `habit.time_frame` directly as the threshold, only as a fallback when `config_history` is empty.

## 2. Add config_history field to habit serializer

- [x] 2.1 In `RecurrentHabitSerializerToRead` (serializers.py), add a `SerializerMethodField` named `config_history` that returns the prefetched `config_history` queryset as a list of dicts: `[{ "effective_from": str, "times": int, "time_frame": str }]` sorted ascending by `effective_from`.
- [x] 2.2 Add `config_history` to the `fields` list in `RecurrentHabitSerializerToRead.Meta`. (Uses `fields = '__all__'` so auto-included.)

## 3. Add prefetch for config_history in all habit views

- [x] 3.1 In `RecurrentHabitApiView.get_queryset()` (api.py), added `Prefetch('config_history', queryset=RecurrentHabitConfigHistory.objects.order_by('effective_from'))`.
- [x] 3.2 In `RecurrentHabitDetailApiView.get_queryset()` (api.py), added the same `config_history` prefetch. Also updated `AllHabitsApiView` single-habit GET path to use a prefetched queryset instead of `get_object_or_404`.
- [x] 3.3 `SpaceHabitsApiView` uses polymorphic `select_subclasses()` which does not support cross-MTI `to_attr` prefetch reliably. Falls back to per-habit DB queries (pre-existing N+1 pattern). Correctness is unaffected.

## 4. Write tests

- [x] 4.1 In `accountability_project/Models/habits/tests.py`, added `ComputeStreakHistoricalConfigTests`: test `times=3→1` scenario asserts `streak["count"] == 0`.
- [x] 4.2 Added test: `times=1→3` scenario, 3 weeks of 1 checkmark each, asserts `streak["count"] == 3`.
- [x] 4.3 Added test: verifies `config_history` field is present and correctly shaped in serializer output.

> **Note:** Tests require PostgreSQL (psycopg2). Run with Docker: `docker-compose up -d db && python manage.py test Models.habits.tests.ComputeStreakHistoricalConfigTests`

## 5. Verify end-to-end

- [x] 5.1 Confirm the `/api/habits/` response includes `config_history` on each habit object.
- [x] 5.2 Confirm the streak count returned is `0` for the scenario where past weeks had a higher target.
- [x] 5.3 Confirm the streak count is unchanged (correct) for habits where the target was never changed.
