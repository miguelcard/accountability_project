## 1. Deferred effective_from logic

- [x] 1.1 In `accountability_project/Models/habits/api/serializers.py`, in `RecurrentHabitSerializerToWrite.update()`, replace the `effective_from` calculation for time_frame changes with a `next_period_start(today, new_time_frame)` helper that returns the first day of next month (W→M) or next Monday (M→W), with special handling when today is already the first day of that period (defer by one additional period).
- [x] 1.2 Ensure the new helper correctly handles December→January rollover for W→M and Sunday/Saturday edge cases for M→W.
- [x] 1.3 Stash the computed `effective_from` and both old/new `time_frame` values on the instance as `instance._config_transition` (a dict) for use in `to_representation()`.

## 2. config_transition response field

- [x] 2.1 In `RecurrentHabitSerializerToRead.to_representation()` (or override `to_representation` on `RecurrentHabitSerializerToWrite`), check if the instance has a `_config_transition` attribute and if so merge it into the output dict as `"config_transition"`.
- [x] 2.2 Verify the field is absent (not present, not null) in responses where `time_frame` did not change (description-only PATCH, times-only PATCH).

## 3. Tests

- [x] 3.1 Add a test: W→M change on May 23 → `effective_from` = June 1, old weekly periods in May 25–31 still earn XP after reconcile.
- [x] 3.2 Add a test: W→M change on June 1 → `effective_from` = July 1, all weeks in June still earn weekly XP.
- [x] 3.3 Add a test: M→W change on May 23 (Saturday) → `effective_from` = May 25.
- [x] 3.4 Add a test: M→W change on Monday May 25 → `effective_from` = June 1 (deferred one full week).
- [x] 3.5 Add a test: PATCH response for W→M includes `config_transition` with correct fields.
- [x] 3.6 Add a test: PATCH response for times-only change does NOT include `config_transition`.
- [x] 3.7 Verify existing serializer integration tests still pass (no regressions in settle/XP logic).

## 4. Verification

- [x] 4.1 Run full test suite (`python manage.py test Models.habits`) and confirm zero failures.
- [x] 4.2 Manually PATCH a habit W→M via the API and verify `config_transition.new_effective_from` is the 1st of next month.
- [x] 4.3 Manually verify that checkmarks added after the PATCH (but before `effective_from`) still earn weekly XP when that week closes.
