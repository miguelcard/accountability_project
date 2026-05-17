import datetime
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from Models.users.models import User
from Models.habits.models import RecurrentHabit, RecurrentHabitConfigHistory, CheckMark, UserXPLedger
from Models.habits.xp_utils import (
    xp_threshold,
    level_from_xp,
    streak_multiplier,
    period_start_for,
    prev_period_start,
    period_end_for,
    _config_for_period,
    compute_streak_for_habit,
    try_award_xp_for_period,
    settle_habit_xp_before_config_change,
    reconcile_user_xp,
)
from Models.habits.api.serializers import RecurrentHabitSerializerToPatch, _compute_streak


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_user(username='testuser_xp') -> User:
    return User.objects.create(
        username=username,
        email=f'{username}@test.com',
        firebase_uid=f'uid_{username}',
    )


def make_weekly_habit(user: User, times: int = 3, title: str = 'XP Habit') -> RecurrentHabit:
    """Creates a weekly habit with created_at set far enough in the past."""
    BACKDATE = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)

    habit = RecurrentHabit.objects.create(
        owner=user, title=title, times=times, time_frame='W'
    )
    # Back-date created_at so reconcile can scan old periods
    RecurrentHabit.objects.filter(pk=habit.pk).update(created_at=BACKDATE)
    # Also back-date the config history row created by the post_save signal
    RecurrentHabitConfigHistory.objects.filter(habit=habit).update(
        effective_from=BACKDATE.date()
    )
    habit.refresh_from_db()
    return habit


def fill_week(habit: RecurrentHabit, monday: datetime.date, count: int | None = None) -> None:
    """Insert `count` DONE checkmarks starting on Monday. Defaults to habit.times."""
    n = count if count is not None else habit.times
    for i in range(n):
        CheckMark.objects.create(
            habit=habit,
            date=monday + datetime.timedelta(days=i),
            status='DONE',
        )


# A fully-closed past Monday (well before today=2026-05-01)
PAST_MONDAY = datetime.date(2026, 4, 20)   # week ends 2026-04-26, fully closed


# ─── Pure-logic tests (no DB writes) ─────────────────────────────────────────

class XPThresholdTests(TestCase):

    def test_level_1_is_zero(self):
        self.assertEqual(xp_threshold(1), 0)

    def test_level_2(self):
        self.assertEqual(xp_threshold(2), 500)

    def test_level_3(self):
        self.assertEqual(xp_threshold(3), 1_100)

    def test_level_4(self):
        self.assertEqual(xp_threshold(4), 1_800)

    def test_level_7(self):
        self.assertEqual(xp_threshold(7), 4_500)

    def test_increasing(self):
        thresholds = [xp_threshold(n) for n in range(1, 11)]
        self.assertEqual(thresholds, sorted(thresholds))


class LevelFromXPTests(TestCase):

    def test_zero_xp_is_level_1(self):
        r = level_from_xp(0)
        self.assertEqual(r['level'], 1)
        self.assertEqual(r['xp_into_level'], 0)

    def test_just_below_level_2(self):
        r = level_from_xp(499)
        self.assertEqual(r['level'], 1)

    def test_exactly_level_2(self):
        r = level_from_xp(500)
        self.assertEqual(r['level'], 2)
        self.assertEqual(r['xp_into_level'], 0)

    def test_just_below_level_3(self):
        r = level_from_xp(1_099)
        self.assertEqual(r['level'], 2)

    def test_exactly_level_3(self):
        r = level_from_xp(1_100)
        self.assertEqual(r['level'], 3)

    def test_level_7_threshold(self):
        r = level_from_xp(4_500)
        self.assertEqual(r['level'], 7)

    def test_pct_to_next_halfway(self):
        # Level 2 gap = 600 (threshold(3)-threshold(2) = 1100-500)
        r = level_from_xp(500 + 300)
        self.assertEqual(r['level'], 2)
        self.assertAlmostEqual(r['pct_to_next'], 0.5, places=3)


class StreakMultiplierTests(TestCase):

    def test_no_streak(self):
        self.assertEqual(streak_multiplier(0), Decimal('1.0'))
        self.assertEqual(streak_multiplier(3), Decimal('1.0'))

    def test_four_week_streak(self):
        self.assertEqual(streak_multiplier(4), Decimal('1.5'))
        self.assertEqual(streak_multiplier(7), Decimal('1.5'))

    def test_eight_week_streak(self):
        self.assertEqual(streak_multiplier(8), Decimal('2.0'))
        self.assertEqual(streak_multiplier(11), Decimal('2.0'))

    def test_cap_at_twelve(self):
        self.assertEqual(streak_multiplier(12), Decimal('2.5'))
        self.assertEqual(streak_multiplier(100), Decimal('2.5'))


class PeriodHelperTests(TestCase):

    def test_period_start_weekly_monday(self):
        monday = datetime.date(2026, 4, 20)
        self.assertEqual(period_start_for(monday, 'W'), monday)

    def test_period_start_weekly_mid_week(self):
        wednesday = datetime.date(2026, 4, 22)
        self.assertEqual(period_start_for(wednesday, 'W'), datetime.date(2026, 4, 20))

    def test_period_start_monthly(self):
        self.assertEqual(
            period_start_for(datetime.date(2026, 4, 15), 'M'),
            datetime.date(2026, 4, 1)
        )

    def test_period_end_weekly(self):
        monday = datetime.date(2026, 4, 20)
        self.assertEqual(period_end_for(monday, 'W'), datetime.date(2026, 4, 26))

    def test_period_end_monthly(self):
        self.assertEqual(
            period_end_for(datetime.date(2026, 4, 1), 'M'),
            datetime.date(2026, 4, 30)
        )

    def test_prev_period_weekly(self):
        monday = datetime.date(2026, 4, 20)
        self.assertEqual(prev_period_start(monday, 'W'), datetime.date(2026, 4, 13))

    def test_prev_period_monthly_crosses_year(self):
        jan = datetime.date(2026, 1, 1)
        self.assertEqual(prev_period_start(jan, 'M'), datetime.date(2025, 12, 1))


# ─── Integration tests (use DB via TestCase transaction rollback) ─────────────

class XPAwardTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.habit = make_weekly_habit(self.user)

    def test_complete_week_awards_xp(self):
        # The post_save signal fires on the 3rd checkmark and awards XP automatically.
        # We verify the ledger entry exists with correct values.
        fill_week(self.habit, PAST_MONDAY)
        entry = UserXPLedger.objects.get(user=self.user, habit=self.habit, period_start=PAST_MONDAY)
        self.assertEqual(entry.xp_awarded, 50)
        self.assertEqual(entry.multiplier, Decimal('1.0'))
        self.assertEqual(entry.streak_at_award, 1)

    def test_incomplete_week_no_xp(self):
        fill_week(self.habit, PAST_MONDAY, count=2)   # needs 3
        awarded = try_award_xp_for_period(self.habit, PAST_MONDAY)
        self.assertFalse(awarded)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)

    def test_idempotency(self):
        fill_week(self.habit, PAST_MONDAY)
        try_award_xp_for_period(self.habit, PAST_MONDAY)
        try_award_xp_for_period(self.habit, PAST_MONDAY)  # second call
        self.assertEqual(UserXPLedger.objects.filter(user=self.user, habit=self.habit).count(), 1)

    def test_streak_multiplier_applied(self):
        """Complete 4 consecutive weeks → streak=4 → ×1.5 → 75 XP on the 4th."""
        mondays = [PAST_MONDAY - datetime.timedelta(weeks=i) for i in range(3, -1, -1)]
        for monday in mondays:
            fill_week(self.habit, monday)
            try_award_xp_for_period(self.habit, monday)

        last_entry = UserXPLedger.objects.get(user=self.user, period_start=PAST_MONDAY)
        self.assertEqual(last_entry.streak_at_award, 4)
        self.assertEqual(last_entry.multiplier, Decimal('1.5'))
        self.assertEqual(last_entry.xp_awarded, 75)

    def test_open_period_not_awarded(self):
        """Checkmarks in the current (still open) week should not earn XP."""
        today = datetime.date.today()
        current_monday = period_start_for(today, 'W')
        fill_week(self.habit, current_monday)
        # Both the signal path and the direct call must refuse to award XP
        awarded = try_award_xp_for_period(self.habit, current_monday)
        self.assertFalse(awarded)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)

    def test_reconcile_fills_missed_periods(self):
        """reconcile_user_xp should result in 2 ledger entries for 2 completed weeks."""
        monday_1 = PAST_MONDAY - datetime.timedelta(weeks=1)
        monday_2 = PAST_MONDAY
        fill_week(self.habit, monday_1)
        fill_week(self.habit, monday_2)
        # Signal may have already created entries; reconcile fills any gaps.
        # Either way, 2 entries must exist after reconcile.
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 2)

    def test_reconcile_is_idempotent(self):
        fill_week(self.habit, PAST_MONDAY)
        reconcile_user_xp(self.user)
        reconcile_user_xp(self.user)   # second call
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

    def test_habit_title_snapshotted(self):
        fill_week(self.habit, PAST_MONDAY)
        try_award_xp_for_period(self.habit, PAST_MONDAY)
        entry = UserXPLedger.objects.get(user=self.user, period_start=PAST_MONDAY)
        self.assertEqual(entry.habit_title_snap, 'XP Habit')

    def test_xp_survives_habit_deletion(self):
        fill_week(self.habit, PAST_MONDAY)
        try_award_xp_for_period(self.habit, PAST_MONDAY)
        habit_pk = self.habit.pk
        self.habit.delete()

        # Ledger row still exists, habit FK is NULL, title snapshot preserved
        entry = UserXPLedger.objects.get(user=self.user, habit__isnull=True)
        self.assertIsNone(entry.habit_id)
        self.assertEqual(entry.habit_title_snap, 'XP Habit')
        self.assertEqual(entry.xp_awarded, 50)


# ─── Config-history: model + signal tests ────────────────────────────────────

class ConfigHistoryCreationTests(TestCase):
    """RecurrentHabitConfigHistory rows are created correctly."""

    def setUp(self):
        self.user = make_user('cfg_user')

    def test_post_save_signal_creates_config_history_on_habit_create(self):
        habit = make_weekly_habit(self.user, times=3)
        rows = RecurrentHabitConfigHistory.objects.filter(habit=habit)
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        self.assertEqual(row.times, 3)
        self.assertEqual(row.time_frame, 'W')

    def test_config_for_period_returns_correct_config(self):
        """_config_for_period returns the row whose effective_from <= period_start."""
        habit = make_weekly_habit(self.user, times=3)
        # Add a second config effective today (use get_or_create because the
        # signal may have already created a row for today when times changed)
        RecurrentHabitConfigHistory.objects.get_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=1, time_frame='W'),
        )
        # Period well in the past → should return the original config (times=3)
        times, tf = _config_for_period(habit, PAST_MONDAY)
        self.assertEqual(times, 3)
        self.assertEqual(tf, 'W')

    def test_config_for_period_returns_new_config_for_future_period(self):
        """After a config change today, periods starting today use the new config."""
        habit = make_weekly_habit(self.user, times=3)
        today = datetime.date.today()
        # Update the existing today row (if signal already created it) or create
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=today,
            defaults=dict(times=1, time_frame='W'),
        )
        times, tf = _config_for_period(habit, today)
        self.assertEqual(times, 1)


# ─── Config-history: XP isolation tests ──────────────────────────────────────

class XPIsolationFromTimesChangeTests(TestCase):
    """
    Lowering `times` must NOT retroactively award XP for past periods
    where the user didn't meet the original requirement.
    """

    def setUp(self):
        self.user = make_user('isolation_user')

    def test_times_decrease_does_not_award_past_un_met_periods(self):
        """
        Habit starts at 3×/week.
        User completes 2 checkmarks in a past week (not enough for 3×).
        Config is lowered to 1×.
        reconcile_user_xp must NOT award XP for that week.
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=2)  # only 2/3 done

        # Simulate a config change: settle + add new config history row
        settle_habit_xp_before_config_change(habit, old_times=3, old_time_frame='W')
        # Record the new config in history
        RecurrentHabitConfigHistory.objects.get_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=1, time_frame='W'),
        )
        # Change the live habit field
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=1)
        habit.refresh_from_db()

        # Reconcile should NOT award XP because under old config (3×), 2 is not enough
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)

    def test_times_decrease_awards_past_period_where_old_req_met(self):
        """
        Habit 3×/week, user did 3 checkmarks in a past week.
        Config lowered to 1×.
        That week was already settled under the old config (3×) → XP awarded.
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=3)  # meets old 3× requirement

        settle_habit_xp_before_config_change(habit, old_times=3, old_time_frame='W')
        RecurrentHabitConfigHistory.objects.get_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=1, time_frame='W'),
        )
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=1)
        habit.refresh_from_db()

        # The settle step should have awarded 50 XP for that week
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

    def test_already_awarded_xp_unaffected_by_times_increase(self):
        """
        XP already in ledger must not be modified when times is increased.
        """
        habit = make_weekly_habit(self.user, times=1)
        fill_week(habit, PAST_MONDAY, count=1)
        try_award_xp_for_period(habit, PAST_MONDAY)

        entry_before = UserXPLedger.objects.get(user=self.user, period_start=PAST_MONDAY)
        xp_before = entry_before.xp_awarded

        # Settle + increase times
        settle_habit_xp_before_config_change(habit, old_times=1, old_time_frame='W')
        RecurrentHabitConfigHistory.objects.get_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=5, time_frame='W'),
        )
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=5)
        habit.refresh_from_db()

        reconcile_user_xp(self.user)

        entry_after = UserXPLedger.objects.get(user=self.user, period_start=PAST_MONDAY)
        self.assertEqual(entry_after.xp_awarded, xp_before)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)


class XPIsolationFromTimeFrameChangeTests(TestCase):
    """
    Changing time_frame (W↔M) must not retroactively affect past period XP.
    """

    def setUp(self):
        self.user = make_user('tf_change_user')

    def test_time_frame_change_weekly_to_monthly_settles_old_weekly_periods(self):
        """
        Habit W 3×/week. Complete a full past week. Settle (W→M config change).
        That week's XP must be awarded under the old weekly config.
        Reconcile after the change must not create any new monthly entries for
        those old weekly periods.
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=3)

        # Settle before W→M change
        settle_habit_xp_before_config_change(habit, old_times=3, old_time_frame='W')
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

        # Record the new monthly config
        RecurrentHabitConfigHistory.objects.get_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=1, time_frame='M'),
        )
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=1, time_frame='M')
        habit.refresh_from_db()

        # Reconcile should not create any extra entries for past weekly periods
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

    def test_time_frame_change_unsettled_weekly_period_not_retroactively_awarded_monthly(self):
        """
        Habit W 3×/week. User did 2/3 in a past week (NOT enough for W).
        No settle is called for that incomplete period.
        After W→M change, reconcile must NOT award XP for that past month
        using the new monthly config (1×/month) based on those same 2 checkmarks.
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=2)  # 2/3 — incomplete under W config

        # Settle past periods under old config (unsettled: 2/3 not enough, so 0 awarded)
        settle_habit_xp_before_config_change(habit, old_times=3, old_time_frame='W')
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)

        # Change to monthly 1×
        RecurrentHabitConfigHistory.objects.get_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=1, time_frame='M'),
        )
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=1, time_frame='M')
        habit.refresh_from_db()

        # Reconcile — must NOT award anything for past weekly period under new monthly rules
        # because the monthly reconcile only walks periods from today's config effective_from onward
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)


class SettleXPBeforeConfigChangeTests(TestCase):
    """Direct tests for settle_habit_xp_before_config_change."""

    def setUp(self):
        self.user = make_user('settle_user')

    def test_settle_awards_completed_past_periods(self):
        """settle should result in XP entries for all completed periods under old config."""
        habit = make_weekly_habit(self.user, times=2)
        monday_1 = PAST_MONDAY - datetime.timedelta(weeks=1)
        monday_2 = PAST_MONDAY
        fill_week(habit, monday_1, count=2)
        fill_week(habit, monday_2, count=2)

        # settle guarantees all past periods are resolved under the old config
        # (some may have already been awarded by the post_save signal — that's fine)
        settle_habit_xp_before_config_change(habit, old_times=2, old_time_frame='W')
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 2)

    def test_settle_skips_incomplete_past_periods(self):
        """settle must not award periods where done_count < old_times."""
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=1)  # only 1/3

        awarded = settle_habit_xp_before_config_change(habit, old_times=3, old_time_frame='W')
        self.assertEqual(awarded, 0)

    def test_settle_is_idempotent(self):
        """Calling settle twice must not double-award."""
        habit = make_weekly_habit(self.user, times=2)
        fill_week(habit, PAST_MONDAY, count=2)

        settle_habit_xp_before_config_change(habit, old_times=2, old_time_frame='W')
        settle_habit_xp_before_config_change(habit, old_times=2, old_time_frame='W')
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)


# ─── Fix #1: same-day double config change via serializer ────────────────────

class SameDayDoubleConfigChangeTests(TestCase):
    """
    If times is changed twice on the same day the second change must win.
    Previously get_or_create was used which silently kept the first value.
    update_or_create must overwrite it.
    """

    def setUp(self):
        self.user = make_user('same_day_user')

    def test_second_same_day_change_overwrites_first(self):
        """
        1st PATCH: times 3 → 1  (creates config row for today with times=1)
        2nd PATCH: times 1 → 5  (must update today's row to times=5)

        Without update_or_create the row stays at times=1 after the 2nd PATCH.
        """
        habit = make_weekly_habit(self.user, times=3)

        # Simulate first config change via serializer (3 → 1)
        serializer = RecurrentHabitSerializerToPatch(
            habit,
            data={'times': 1},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        habit.refresh_from_db()
        self.assertEqual(habit.times, 1)

        # Simulate second same-day config change (1 → 5)
        serializer2 = RecurrentHabitSerializerToPatch(
            habit,
            data={'times': 5},
            partial=True,
        )
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        serializer2.save()
        habit.refresh_from_db()

        # The today config history row must reflect the latest value (5)
        today_row = RecurrentHabitConfigHistory.objects.get(
            habit=habit, effective_from=datetime.date.today()
        )
        self.assertEqual(today_row.times, 5)
        # And the live habit reflects it too
        self.assertEqual(habit.times, 5)

    def test_same_day_change_does_not_create_duplicate_config_rows(self):
        """Only one config row per day must exist, regardless of how many changes."""
        habit = make_weekly_habit(self.user, times=3)

        for new_times in [1, 2, 4]:
            serializer = RecurrentHabitSerializerToPatch(
                habit,
                data={'times': new_times},
                partial=True,
            )
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()
            habit.refresh_from_db()

        today_rows = RecurrentHabitConfigHistory.objects.filter(
            habit=habit, effective_from=datetime.date.today()
        )
        self.assertEqual(today_rows.count(), 1)
        self.assertEqual(today_rows.first().times, 4)


# ─── Fix #2: settle uses most-recent config row (cycling configs) ─────────────

class SettleCyclingConfigTests(TestCase):
    """
    When a config value cycles (e.g. 3→1→3), settle must use the *most-recent*
    config row for the old value so it only settles the current window, not the
    entire history back to creation.
    """

    def setUp(self):
        self.user = make_user('cycle_user')

    def test_settle_after_cycling_config_uses_most_recent_window(self):
        """
        Timeline:
          Creation (Jan 1): times=3
          Week A (PAST_MONDAY-2w): 3 checkmarks done → should earn XP under original config
          Change to times=1 (settled, week A XP awarded)
          Change back to times=3 (another settle; week B done 3×)
          Week B (PAST_MONDAY-1w): 3 checkmarks done → XP should be awarded

        After the second settle (back to times=3) settle_habit_xp_before_config_change
        must only look back from the *second* times=3 effective_from, not from Jan 1.
        This means week A (which was already settled under times=1→3 window) is not
        re-evaluated, and the total ledger count is exactly 2.
        """
        habit = make_weekly_habit(self.user, times=3)
        week_a = PAST_MONDAY - datetime.timedelta(weeks=2)
        week_b = PAST_MONDAY - datetime.timedelta(weeks=1)

        # --- Phase 1: fill week A, settle under original times=3, then change to 1 ---
        fill_week(habit, week_a, count=3)
        settle_habit_xp_before_config_change(habit, old_times=3, old_time_frame='W')

        mid_date = week_a + datetime.timedelta(weeks=1)  # a date between week A and B
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=mid_date,
            defaults=dict(times=1, time_frame='W'),
        )
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=1)
        habit.refresh_from_db()

        # --- Phase 2: fill week B (1 checkmark is enough for times=1) ---
        fill_week(habit, week_b, count=1)
        # Settle under times=1 before going back to 3
        settle_habit_xp_before_config_change(habit, old_times=1, old_time_frame='W')

        # Record another times=3 config (today)
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=datetime.date.today(),
            defaults=dict(times=3, time_frame='W'),
        )
        RecurrentHabit.objects.filter(pk=habit.pk).update(times=3)
        habit.refresh_from_db()

        # --- Verify: exactly 2 XP ledger entries exist (week A and week B) ---
        ledger_count = UserXPLedger.objects.filter(user=self.user).count()
        self.assertEqual(ledger_count, 2)

        # And reconcile must not create any extra entries
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 2)


# ─── Fix #3: compute_streak_for_habit time_frame_override avoids extra query ──

class StreakTimeFrameOverrideTests(TestCase):
    """
    compute_streak_for_habit(time_frame_override=...) must produce the same
    streak count as when the time_frame is looked up from config history,
    and must accept the parameter without error.
    """

    def setUp(self):
        self.user = make_user('streak_override_user')

    def test_time_frame_override_gives_same_result_as_lookup(self):
        """Result with override must equal result without."""
        habit = make_weekly_habit(self.user, times=2)
        fill_week(habit, PAST_MONDAY - datetime.timedelta(weeks=1), count=2)
        fill_week(habit, PAST_MONDAY, count=2)
        # Award both weeks to create ledger rows
        try_award_xp_for_period(habit, PAST_MONDAY - datetime.timedelta(weeks=1))
        try_award_xp_for_period(habit, PAST_MONDAY)

        streak_via_lookup   = compute_streak_for_habit(habit, PAST_MONDAY)
        streak_via_override = compute_streak_for_habit(
            habit, PAST_MONDAY, time_frame_override='W'
        )
        self.assertEqual(streak_via_lookup, streak_via_override)
        self.assertEqual(streak_via_lookup, 2)

    def test_wrong_time_frame_override_resets_streak(self):
        """Passing time_frame='M' when ledger has weekly entries means no monthly
        period_start matches → streak should be 1 (just the current period)."""
        habit = make_weekly_habit(self.user, times=2)
        fill_week(habit, PAST_MONDAY - datetime.timedelta(weeks=1), count=2)
        fill_week(habit, PAST_MONDAY, count=2)
        try_award_xp_for_period(habit, PAST_MONDAY - datetime.timedelta(weeks=1))
        try_award_xp_for_period(habit, PAST_MONDAY)

        # Monthly walk-back won't find the weekly period_starts in the ledger
        streak_monthly = compute_streak_for_habit(
            habit, PAST_MONDAY, time_frame_override='M'
        )
        self.assertEqual(streak_monthly, 1)


# ─── Fix #4: RecurrentHabitConfigHistory.time_frame choices validation ────────

class ConfigHistoryChoicesValidationTests(TestCase):
    """
    RecurrentHabitConfigHistory.time_frame must enforce the same choices as
    RecurrentHabit.time_frame ('W' or 'M').
    Invalid values must be rejected at full_clean() / form validation.
    """

    def setUp(self):
        self.user = make_user('choices_user')

    def test_valid_time_frame_choices_are_accepted(self):
        habit = make_weekly_habit(self.user, times=1)
        for tf in ('W', 'M'):
            row = RecurrentHabitConfigHistory(
                habit=habit,
                times=1,
                time_frame=tf,
                effective_from=datetime.date(2025, 1, 1),
            )
            try:
                row.full_clean()  # should not raise
            except ValidationError as e:
                self.fail(f'full_clean() raised ValidationError for valid time_frame={tf!r}: {e}')

    def test_invalid_time_frame_rejected_by_full_clean(self):
        habit = make_weekly_habit(self.user, times=1)
        row = RecurrentHabitConfigHistory(
            habit=habit,
            times=1,
            time_frame='X',  # invalid
            effective_from=datetime.date(2025, 1, 1),
        )
        with self.assertRaises(ValidationError):
            row.full_clean()


# ─── Fix #8: serializer-level integration test for XP isolation ───────────────

class SerializerXPIsolationIntegrationTests(TestCase):
    """
    End-to-end: exercise the serializer update() path (not just the util
    functions directly) and verify that XP isolation holds.
    """

    def setUp(self):
        self.user = make_user('serializer_xp_user')

    def test_patch_times_down_via_serializer_does_not_award_unmet_past_periods(self):
        """
        2/3 checkmarks in a past week.  PATCH times to 1 via serializer.
        That past week must NOT be retroactively awarded (2 < 3 under old config).
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=2)

        serializer = RecurrentHabitSerializerToPatch(
            habit, data={'times': 1}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # Must be zero: the settle ran under old times=3, 2 < 3 → not awarded
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)

        # And reconcile must not pick it up under the new times=1 either
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 0)

    def test_patch_times_down_via_serializer_does_award_met_past_periods(self):
        """
        3/3 checkmarks in a past week.  PATCH times to 1 via serializer.
        That week WAS met under old config → settle must award it.
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=3)

        serializer = RecurrentHabitSerializerToPatch(
            habit, data={'times': 1}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # Settle during update() must have awarded the week
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

    def test_patch_time_frame_change_via_serializer_settles_old_frame_first(self):
        """
        Complete a past week (3/3).  PATCH time_frame W→M.
        The settle inside update() must award the weekly XP before switching frames.
        """
        habit = make_weekly_habit(self.user, times=3)
        fill_week(habit, PAST_MONDAY, count=3)

        serializer = RecurrentHabitSerializerToPatch(
            habit, data={'time_frame': 'M', 'times': 1}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # Weekly XP must have been awarded during the settle step
        entry = UserXPLedger.objects.filter(user=self.user).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.reason, 'WEEKLY_HABIT')

        # After the change, reconcile must not create any extra monthly entries
        # for the same underlying checkmarks
        reconcile_user_xp(self.user)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

    def test_patch_config_creates_correct_config_history_row(self):
        """After a PATCH the new config must be recorded in history."""
        habit = make_weekly_habit(self.user, times=3)

        serializer = RecurrentHabitSerializerToPatch(
            habit, data={'times': 2}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        today_row = RecurrentHabitConfigHistory.objects.get(
            habit=habit, effective_from=datetime.date.today()
        )
        self.assertEqual(today_row.times, 2)
        self.assertEqual(today_row.time_frame, 'W')

    def test_patch_no_config_change_does_not_create_new_history_row(self):
        """A PATCH that only changes title must not add a config history row."""
        habit = make_weekly_habit(self.user, times=3)
        row_count_before = RecurrentHabitConfigHistory.objects.filter(habit=habit).count()

        serializer = RecurrentHabitSerializerToPatch(
            habit, data={'title': 'New title'}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        row_count_after = RecurrentHabitConfigHistory.objects.filter(habit=habit).count()
        self.assertEqual(row_count_before, row_count_after)


# ─── Settle / reconcile award periods oldest→newest (streak ordering fix) ────

class SettleStreakOrderingTests(TestCase):
    """
    When settle_habit_xp_before_config_change processes multiple consecutive
    completed periods it must award them oldest→newest so that each period's
    streak_at_award correctly reflects the running streak.

    Before the fix, periods were awarded newest→oldest, meaning the oldest
    period was written last — when all earlier periods were already in the
    ledger — so its streak was inflated, while the newest period was written
    first with streak=1 (nothing in ledger yet). The ledger would show e.g.
    streak 1, 1, 3 instead of the correct 1, 2, 3.
    """

    def setUp(self):
        self.user = make_user('settle_order_user')

    def test_settle_awards_oldest_period_first_so_streak_increments(self):
        """
        Three consecutive completed weeks settled at once must produce
        streak_at_award values of 1, 2, 3 (not 1, 1, 1 or 3, 2, 1).
        """
        habit = make_weekly_habit(self.user, times=1)
        w1 = PAST_MONDAY - datetime.timedelta(weeks=2)
        w2 = PAST_MONDAY - datetime.timedelta(weeks=1)
        w3 = PAST_MONDAY

        fill_week(habit, w1, count=1)
        fill_week(habit, w2, count=1)
        fill_week(habit, w3, count=1)

        # Wipe signal-awarded XP so settle has to process all 3 periods fresh.
        UserXPLedger.objects.filter(user=self.user).delete()

        settle_habit_xp_before_config_change(habit, old_times=1, old_time_frame='W')

        entries = list(
            UserXPLedger.objects.filter(user=self.user)
            .order_by('period_start')
            .values_list('period_start', 'streak_at_award')
        )
        self.assertEqual(len(entries), 3)
        period_starts = [e[0] for e in entries]
        streaks       = [e[1] for e in entries]

        self.assertEqual(period_starts, [w1, w2, w3])
        self.assertEqual(streaks, [1, 2, 3])

    def test_settle_streak_reaches_multiplier_threshold(self):
        """
        Four consecutive completed weeks must produce streaks 1,2,3,4 and the
        4th week must use the ×1.5 multiplier (streak ≥ 4).
        """
        habit = make_weekly_habit(self.user, times=1)
        w1 = PAST_MONDAY - datetime.timedelta(weeks=3)
        w2 = PAST_MONDAY - datetime.timedelta(weeks=2)
        w3 = PAST_MONDAY - datetime.timedelta(weeks=1)
        w4 = PAST_MONDAY

        for w in (w1, w2, w3, w4):
            fill_week(habit, w, count=1)

        # Wipe signal-awarded XP so settle processes all 4 periods fresh.
        UserXPLedger.objects.filter(user=self.user).delete()

        settle_habit_xp_before_config_change(habit, old_times=1, old_time_frame='W')

        entries = list(
            UserXPLedger.objects.filter(user=self.user)
            .order_by('period_start')
            .values_list('period_start', 'streak_at_award', 'xp_awarded')
        )
        self.assertEqual(len(entries), 4)
        streaks = [e[1] for e in entries]
        xp_vals = [e[2] for e in entries]

        self.assertEqual(streaks, [1, 2, 3, 4])
        # First 3 weeks: ×1.0 = 50; 4th week: ×1.5 = 75
        self.assertEqual(xp_vals, [50, 50, 50, 75])


class ReconcileStreakOrderingTests(TestCase):
    """
    reconcile_user_xp must also award periods oldest→newest so streak values
    are correct when it back-fills missed periods.
    """

    def setUp(self):
        self.user = make_user('reconcile_order_user')

    def test_reconcile_awards_oldest_period_first_so_streak_increments(self):
        """
        Three consecutive completed weeks with no prior XP entries should
        produce streak_at_award 1, 2, 3 after reconcile.

        fill_week triggers the checkmark signal which awards XP immediately,
        so we delete those ledger rows first to simulate the scenario where
        checkmarks were added without triggering XP (e.g. direct DB inserts).
        Reconcile is then the catch-up mechanism.
        """
        habit = make_weekly_habit(self.user, times=1)
        w1 = PAST_MONDAY - datetime.timedelta(weeks=2)
        w2 = PAST_MONDAY - datetime.timedelta(weeks=1)
        w3 = PAST_MONDAY

        fill_week(habit, w1, count=1)
        fill_week(habit, w2, count=1)
        fill_week(habit, w3, count=1)

        # Wipe any XP already awarded by the signal so reconcile starts fresh.
        UserXPLedger.objects.filter(user=self.user).delete()

        awarded = reconcile_user_xp(self.user)
        self.assertEqual(awarded, 3)

        entries = list(
            UserXPLedger.objects.filter(user=self.user)
            .order_by('period_start')
            .values_list('period_start', 'streak_at_award')
        )
        period_starts = [e[0] for e in entries]
        streaks       = [e[1] for e in entries]

        self.assertEqual(period_starts, [w1, w2, w3])
        self.assertEqual(streaks, [1, 2, 3])

    def test_reconcile_streak_reaches_multiplier_threshold(self):
        """
        Four consecutive completed weeks reconciled at once must produce
        streak 4 on the last entry and award 75 XP (×1.5).
        """
        habit = make_weekly_habit(self.user, times=1)
        w1 = PAST_MONDAY - datetime.timedelta(weeks=3)
        w2 = PAST_MONDAY - datetime.timedelta(weeks=2)
        w3 = PAST_MONDAY - datetime.timedelta(weeks=1)
        w4 = PAST_MONDAY

        for w in (w1, w2, w3, w4):
            fill_week(habit, w, count=1)

        # Wipe signal-awarded XP so reconcile processes all 4 periods fresh.
        UserXPLedger.objects.filter(user=self.user).delete()

        reconcile_user_xp(self.user)

        entries = list(
            UserXPLedger.objects.filter(user=self.user)
            .order_by('period_start')
            .values_list('streak_at_award', 'xp_awarded')
        )
        streaks = [e[0] for e in entries]
        xp_vals = [e[1] for e in entries]

        self.assertEqual(streaks, [1, 2, 3, 4])
        self.assertEqual(xp_vals, [50, 50, 50, 75])


# ─── Test 5: new config governs only periods starting after effective_from ───

class NewConfigAppliesToFuturePeriodsOnlyTests(TestCase):
    """
    After a config change to 3×/week (effective today), a closed week whose
    period_start < today is still evaluated under the OLD config.  A closed
    week whose period_start >= effective_from is evaluated under the NEW config.

    This verifies that the config-history lookup correctly gates which rule
    applies to each period.
    """

    def setUp(self):
        self.user = make_user('future_config_user')

    def test_insufficient_checkmarks_under_new_config_earn_no_xp(self):
        """
        Habit starts at 1×/week.  Config changed to 3×/week with effective_from
        set to the start of a past closed week W2.  W2 has only 2 checkmarks.
        Expected: no XP for W2 (2 < 3 under new config).
        """
        habit = make_weekly_habit(self.user, times=1)

        w1 = PAST_MONDAY - datetime.timedelta(weeks=1)  # old config week
        w2 = PAST_MONDAY                                  # new config week

        # Put old config covering w1 (initial row covers everything up to w2)
        # Now insert a new config row effective from w2 with times=3
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=w2,
            defaults=dict(times=3, time_frame='W'),
        )

        # Complete w1 fully under old rule (1×/week) → should earn XP
        fill_week(habit, w1, count=1)
        try_award_xp_for_period(habit, w1)
        xp_after_w1 = UserXPLedger.objects.filter(user=self.user).count()
        self.assertEqual(xp_after_w1, 1)

        # In w2 (governed by new 3×/week rule): only 2 checkmarks — NOT enough
        fill_week(habit, w2, count=2)
        awarded = try_award_xp_for_period(habit, w2)

        self.assertFalse(awarded)
        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)

    def test_sufficient_checkmarks_under_new_config_earn_xp(self):
        """
        Same setup but W2 has 3 checkmarks (meets the new 3×/week requirement).
        Expected: XP IS awarded for W2 (either by the signal on the 3rd
        checkmark or by a subsequent try_award_xp_for_period call).
        """
        habit = make_weekly_habit(self.user, times=1)
        w2 = PAST_MONDAY

        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=w2,
            defaults=dict(times=3, time_frame='W'),
        )

        fill_week(habit, w2, count=3)
        # Signal fires on the 3rd checkmark and awards XP; the explicit call
        # is idempotent (returns False = already awarded), but XP exists.
        try_award_xp_for_period(habit, w2)

        self.assertEqual(UserXPLedger.objects.filter(user=self.user).count(), 1)


# ─── Historical streak tests ─────────────────────────────────────────────────

class ComputeStreakHistoricalConfigTests(TestCase):
    """
    Tests that _compute_streak correctly evaluates each past period against
    the `times` value that was in effect during that period, not the current
    live value. Uses RecurrentHabitConfigHistory to record target changes.
    """

    def setUp(self):
        self.user = make_user('streak_hist_user')

    def _monday(self, weeks_ago: int) -> datetime.date:
        """Return the Monday of the week `weeks_ago` weeks before today."""
        today = datetime.date.today()
        this_monday = today - datetime.timedelta(days=today.weekday())
        return this_monday - datetime.timedelta(weeks=weeks_ago)

    def test_increasing_times_does_not_inflate_past_streak(self):
        """
        Habit had times=3 for the past 2 weeks. User completed it 1x each week
        (not meeting the goal of 3). User then changes times to 1.
        _compute_streak should return 0 because those weeks did not meet
        the goal of 3 that was in effect at the time.
        """
        habit = make_weekly_habit(self.user, times=1)  # creates with times=1, then we set history

        w2 = self._monday(weeks_ago=2)
        w1 = self._monday(weeks_ago=1)

        # Simulate that the habit had times=3 for those two past weeks
        RecurrentHabitConfigHistory.objects.filter(habit=habit).update(
            effective_from=w2, times=3, time_frame='W'
        )

        # User completed it only 1x each of the past two weeks
        CheckMark.objects.create(habit=habit, date=w2, status='DONE')
        CheckMark.objects.create(habit=habit, date=w1, status='DONE')

        # Now simulate times changed to 1 this week
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=self._monday(weeks_ago=0),
            defaults=dict(times=1, time_frame='W'),
        )
        habit.times = 1
        habit.save()

        result = _compute_streak(habit)
        self.assertEqual(
            result['count'], 0,
            msg="Changing times from 3 to 1 should NOT retroactively make "
                "past weeks with only 1 checkmark count as complete (they needed 3)."
        )

    def test_decreasing_times_does_not_invalidate_past_streak(self):
        """
        Habit had times=1 for 3 consecutive past weeks. User completed it
        1x each week (meeting the goal of 1). User then changes times to 3.
        _compute_streak should still return 3 because those weeks DID meet
        the goal of 1 that was in effect at the time.
        """
        habit = make_weekly_habit(self.user, times=3)  # now times=3, but history reflects old config

        w3 = self._monday(weeks_ago=3)
        w2 = self._monday(weeks_ago=2)
        w1 = self._monday(weeks_ago=1)

        # Simulate habit had times=1 for those three weeks
        RecurrentHabitConfigHistory.objects.filter(habit=habit).update(
            effective_from=w3, times=1, time_frame='W'
        )

        # User completed it 1x each week (met the goal of 1)
        CheckMark.objects.create(habit=habit, date=w3, status='DONE')
        CheckMark.objects.create(habit=habit, date=w2, status='DONE')
        CheckMark.objects.create(habit=habit, date=w1, status='DONE')

        # Now simulate times changed to 3 this week
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=self._monday(weeks_ago=0),
            defaults=dict(times=3, time_frame='W'),
        )

        result = _compute_streak(habit)
        self.assertEqual(
            result['count'], 3,
            msg="Changing times from 1 to 3 should NOT invalidate past weeks "
                "where 1 checkmark met the goal of 1 that was in effect then."
        )

    def test_config_history_field_in_serializer_output(self):
        """
        RecurrentHabitSerializerToRead includes a `config_history` field
        listing all config snapshots sorted ascending by effective_from,
        each with effective_from (ISO string), times (int), time_frame (str).
        """
        habit = make_weekly_habit(self.user, times=1)

        w3 = self._monday(weeks_ago=3)
        # Simulate a second config change
        RecurrentHabitConfigHistory.objects.update_or_create(
            habit=habit,
            effective_from=w3 + datetime.timedelta(weeks=2),
            defaults=dict(times=3, time_frame='W'),
        )

        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user

        from Models.habits.api.serializers import RecurrentHabitSerializerToRead
        data = RecurrentHabitSerializerToRead(habit, context={'request': request}).data

        self.assertIn('config_history', data, "config_history field must be present in serializer output")
        history = data['config_history']
        self.assertIsInstance(history, list, "config_history must be a list")
        self.assertGreaterEqual(len(history), 1, "config_history must have at least one entry")

        for entry in history:
            self.assertIn('effective_from', entry)
            self.assertIn('times', entry)
            self.assertIn('time_frame', entry)
            self.assertIsInstance(entry['times'], int)

        # Verify ascending sort by effective_from
        dates = [entry['effective_from'] for entry in history]
        self.assertEqual(dates, sorted(dates), "config_history must be sorted ascending by effective_from")
