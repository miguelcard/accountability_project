## Context

`_compute_streak()` in `accountability_project/Models/habits/api/serializers.py` computes the streak badge returned with every habit. It walks backwards week-by-week and counts consecutive periods where `DONE` checkmarks ≥ `habit.times`. It uses `habit.times` (the current live value) for every period in the walk — including past periods where a different target was in effect.

`RecurrentHabitConfigHistory` already records every target change with an `effective_from` date. `_config_for_period(habit, period_start)` in `xp_utils.py` already resolves the correct `(times, time_frame)` for any past date — the XP system uses this. The streak serializer just needs to do the same.

A second gap: the frontend's progress bar needs the historical target for past weeks. The habit API response currently only includes the live `times`. Adding `config_history` as a serialized field solves this without a new endpoint.

## Goals / Non-Goals

**Goals:**
- `_compute_streak()` evaluates each past period against the target that was in effect during that period, using `_config_for_period`.
- `RecurrentHabitSerializerToRead` includes a `config_history` field (list of `{effective_from, times, time_frame}`, ascending).
- All views that serve habits prefetch `config_history` to prevent N+1 queries.

**Non-Goals:**
- Changing the `RecurrentHabitConfigHistory` model or migration.
- Changing how config history rows are created (signals already handle this correctly).
- Any XP recalculation or data backfill.
- Changing the streak response shape (still `{ count, unit }`).

## Decisions

### Decision 1: Reuse `_config_for_period` directly in `_compute_streak`

**Chosen:** In each loop iteration of `_compute_streak`, call `_config_for_period(habit, period_start)` to get `(required, time_frame)` for that period instead of using the live `habit.times` / `habit.time_frame`.

**Alternative considered:** Duplicate the history lookup inline. Rejected — `_config_for_period` already has the correct fallback logic and is tested. Reuse avoids drift.

**Note on performance:** `_config_for_period` currently issues a DB query per call. Since `_compute_streak` walks backwards multiple periods, this could become multiple queries per habit. Mitigation: the prefetch of `config_history` loaded on the habit object can be used instead of hitting the DB — either by checking `habit.recurrenthabitconfighistory_set.all()` (prefetched) or by passing the prefetch list into `_config_for_period`. Simplest first approach: use the prefetched queryset directly inside `_compute_streak` without modifying `_config_for_period`.

### Decision 2: `config_history` as an inline serializer field, not a nested endpoint

**Chosen:** Add a `SerializerMethodField` on `RecurrentHabitSerializerToRead` that returns the prefetched `config_history` rows as a list of dicts.

**Alternative considered:** A separate `/api/habits/{id}/config-history/` endpoint. Rejected — clients would need an extra request per habit to get the history. Inline is simpler and the data is small.

### Decision 3: Prefetch `config_history` in all habit views

The related name on `RecurrentHabitConfigHistory` → `RecurrentHabit` is `recurrenthabitconfighistory_set` (or whatever `related_name` is set). Prefetch via `Prefetch('recurrenthabitconfighistory_set', queryset=RecurrentHabitConfigHistory.objects.order_by('effective_from'))` so the list arrives pre-sorted and no extra DB hit occurs in `_compute_streak` or the serializer field.

### Decision 4: Fallback when no history rows exist

If `_config_for_period` returns no row (pre-feature data), it already falls back to the current live `habit.times`. This is the correct behavior for forward-only correctness and requires no additional handling.

## Risks / Trade-offs

- [Risk] `_config_for_period` issues a DB query if called without a prefetch → Mitigation: Use the prefetched related manager within `_compute_streak` to avoid DB calls per period iteration. Concretely: pass the sorted prefetched list into the streak computation loop rather than relying on `_config_for_period`'s ORM call.
- [Risk] `related_name` on `RecurrentHabitConfigHistory` might differ → Mitigation: verify exact `related_name` in models.py before coding.
- [Trade-off] `config_history` increases serializer output size → Negligible (typically 1–5 rows of 3 small fields per habit).
- [Trade-off] Old data with no config history rows gets live `times` as fallback → Acceptable; app is pre-production.

## Open Questions

- Confirm the exact `related_name` used on `RecurrentHabitConfigHistory.habit` FK to use the correct prefetch key.
