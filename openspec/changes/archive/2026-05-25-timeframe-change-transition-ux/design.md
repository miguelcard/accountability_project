## Context

When a `RecurrentHabit` has its `time_frame` changed (W→M or M→W), `RecurrentHabitSerializerToWrite.update()` currently writes a new `RecurrentHabitConfigHistory` row with `effective_from = today`. This means the new rule is eligible to be evaluated immediately. For W→M the next monthly period doesn't close until the 1st of next month — creating a dead zone of up to ~3.5 weeks where no XP can be earned under either rule. For M→W the week that started before the change is treated as the first weekly window which is less disruptive but still inconsistent.

The fix is to defer `effective_from` to the first day of the next full period under the **new** `time_frame`. Old XP continues to accrue under the old rule through the remainder of the current old-rule period. No XP is lost and no ledger rows need modification. Additionally, the PATCH response must surface `config_transition` data so the frontend can show the user exactly when the new rule begins.

## Goals / Non-Goals

**Goals:**
- Eliminate the dead zone by extending the old rule through the end of its current period.
- Expose `config_transition` in the PATCH response when `time_frame` changes.
- Cover both directions: W→M and M→W.
- Handle edge cases: change on day 1 of month (W→M defers a full extra month), change on a Monday (M→W defers exactly one week).

**Non-Goals:**
- Retroactively re-evaluating or clawing back already-awarded XP.
- Changing the `times`-only change path (no time_frame change) — that path still backdates to current period start and is unaffected.
- Any frontend changes (handled in the companion frontend change).
- Changes to `reconcile_user_xp` logic — it already evaluates periods according to config windows correctly.

## Decisions

### 1. Deferred `effective_from` formula

When `time_frame` changes, set:
```
effective_from = next_period_start(today, new_time_frame)
```
where `next_period_start` is defined as:
- **W→M**: `date(today.year, today.month + 1, 1)` — the 1st of next month (handling December rollover)
- **M→W**: `today + timedelta(days=(7 - today.weekday()))` — the coming Monday (next week start)

Special cases:
- If today is already the first day of the new period (e.g. W→M on June 1, or M→W on a Monday), defer by one full period further. We never want `effective_from = today` for a time_frame change because that re-introduces an immediate partial-period ambiguity.

**Alternative considered:** `effective_from = today` (current behaviour). Rejected — creates dead zone.
**Alternative considered:** `effective_from = start of current new-frame period` (e.g. May 1 for a W→M change in May). Rejected — old weekly XP may have already been awarded for weeks in May; the monthly window would overlap with settled periods and the uniqueness constraint on `(habit, effective_from)` would collide.

### 2. `config_transition` in PATCH response

When `time_frame` changes, `to_representation()` (or a custom response wrapper) includes a top-level field alongside the habit data:
```json
"config_transition": {
  "old_time_frame": "W",
  "new_time_frame": "M",
  "new_effective_from": "2026-06-01"
}
```
This field is **absent** (not null) when `time_frame` did not change.

**How**: The serializer's `update()` method computes and stashes `config_transition` on the instance as a transient attribute (e.g. `instance._config_transition`). `to_representation()` reads it if present and merges it into the output dict.

**Alternative considered:** A separate dedicated endpoint for transition metadata. Rejected — unnecessary round-trip; the PATCH already has all required information.

### 3. `settle_habit_xp_before_config_change` call is unaffected

`settle()` is still called before saving the new config row, exactly as today. It settles all closed periods under the old config. Since `effective_from` is now deferred to next month/week, the old config window in `reconcile_user_xp` extends through the remainder of the current period — meaning weeks/months between today and `effective_from` will continue to be evaluated under the old rule on the next reconcile run. No changes needed to `settle()` or `reconcile_user_xp`.

## Risks / Trade-offs

- [Changing W→M on June 1 defers to July 1 — user waits a full month] → Mitigated: this is actually correct behaviour (the user is mid-month, the old weekly rule covers June), and the `config_transition` field lets the frontend explain this clearly.
- [Two time_frame changes in the same day could collide on the `update_or_create` key] → Same risk as today; `update_or_create(habit=instance, effective_from=effective_from)` overwrites the earlier same-day row. Acceptable since `effective_from` is now a future date, not today.
- [M→W: if changed on a Monday, effective_from jumps a full week] → Minor: the current month still earns monthly XP when it closes; the user doesn't lose a week's xp opportunity, they just start weekly tracking slightly later. Fine.

## Migration Plan

No schema migrations. No data migrations. The change is purely in application logic — existing `RecurrentHabitConfigHistory` rows are unaffected. Deploy is safe to roll out at any time.

Rollback: revert the serializer change. Existing config rows with future `effective_from` dates will continue to function correctly under the old logic (they'll just delay the new rule slightly until the next reconcile — acceptable for a rollback window).

## Open Questions

_(none — all decisions resolved during exploration)_
