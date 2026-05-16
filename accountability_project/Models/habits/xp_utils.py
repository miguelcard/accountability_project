"""
XP & Level utilities for the accountability project.

XP rules
--------
- Base XP per completed weekly habit:  50
- Base XP per completed monthly habit: 175
- Streak multiplier (in *periods* of the habit's time_frame):
    < 4   → ×1.0
    4–7   → ×1.5
    8–11  → ×2.0
    ≥ 12  → ×2.5  (cap)

Level thresholds
----------------
Gap from level n to n+1 = 500 + (n-1) × 100
  L1→L2: 500, L2→L3: 600, L3→L4: 700, …

Total XP to reach level n  =  Σ_{i=1}^{n-1} [500 + (i-1)×100]
                            =  (n-1)(400 + 50n)

Period definition
-----------------
Weekly habits  → period_start = Monday of the week
Monthly habits → period_start = 1st of the month

Config-history contract
-----------------------
Every time `times` or `time_frame` changes on a RecurrentHabit a new
RecurrentHabitConfigHistory row is written (effective_from = today).
Before saving the new config, `settle_habit_xp_before_config_change` is called
to award any un-awarded past periods under the *old* config, so that
historical XP is never affected by future config changes.

When evaluating whether a period earned XP we always look up the config that
was in effect at `period_start` via `_config_for_period`.
"""

from __future__ import annotations

import datetime
import logging
from decimal import Decimal

from django.db.models import Count, Q

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────
# Level maths
# ────────────────────────────────────────────────────────────────────────────

def xp_threshold(level: int) -> int:
    """Total XP required to *reach* `level` (level 1 = 0 XP)."""
    if level <= 1:
        return 0
    n = level
    return (n - 1) * (400 + 50 * n)


def level_from_xp(total_xp: int) -> dict:
    """
    Given a total XP amount, return a dict with:
      - level          (int)   current level
      - xp_into_level  (int)   XP accumulated since reaching this level
      - xp_for_level   (int)   total XP gap needed to advance to next level
      - pct_to_next    (float) percentage progress 0.0–1.0
    """
    level = 1
    while True:
        next_threshold = xp_threshold(level + 1)
        if total_xp < next_threshold:
            current_threshold = xp_threshold(level)
            xp_into = total_xp - current_threshold
            xp_needed = next_threshold - current_threshold
            return {
                'level': level,
                'xp_into_level': xp_into,
                'xp_for_level': xp_needed,
                'pct_to_next': round(xp_into / xp_needed, 4) if xp_needed else 1.0,
            }
        level += 1


# ────────────────────────────────────────────────────────────────────────────
# Streak multiplier
# ────────────────────────────────────────────────────────────────────────────

def streak_multiplier(streak: int) -> Decimal:
    if streak >= 12:
        return Decimal('2.5')
    if streak >= 8:
        return Decimal('2.0')
    if streak >= 4:
        return Decimal('1.5')
    return Decimal('1.0')


# ────────────────────────────────────────────────────────────────────────────
# Period helpers
# ────────────────────────────────────────────────────────────────────────────

def period_start_for(date: datetime.date, time_frame: str) -> datetime.date:
    """Return the canonical period_start for a given date and time_frame."""
    if time_frame == 'W':
        return date - datetime.timedelta(days=date.weekday())  # Monday
    # Monthly
    return date.replace(day=1)


def prev_period_start(period_start: datetime.date, time_frame: str) -> datetime.date:
    """Return the period_start immediately before `period_start`."""
    if time_frame == 'W':
        return period_start - datetime.timedelta(weeks=1)
    # Monthly: go back one month
    if period_start.month == 1:
        return period_start.replace(year=period_start.year - 1, month=12)
    return period_start.replace(month=period_start.month - 1)


def period_end_for(period_start: datetime.date, time_frame: str) -> datetime.date:
    """Return the last day (inclusive) of the period."""
    if time_frame == 'W':
        return period_start + datetime.timedelta(days=6)
    # Last day of the month
    if period_start.month == 12:
        return period_start.replace(year=period_start.year + 1, month=1, day=1) - datetime.timedelta(days=1)
    return period_start.replace(month=period_start.month + 1, day=1) - datetime.timedelta(days=1)


# ────────────────────────────────────────────────────────────────────────────
# Config-history lookup
# ────────────────────────────────────────────────────────────────────────────

def _config_for_period(habit, period_start: datetime.date) -> tuple:
    """
    Return (times, time_frame) that was in effect on `period_start`.

    Looks for the most-recent RecurrentHabitConfigHistory row where
    effective_from <= period_start.  Falls back to the oldest known config
    row (creation-time snapshot) if no row covers the period (shouldn't
    happen in normal operation).  As a last resort returns the current live
    values on the habit object.
    """
    from Models.habits.models import RecurrentHabitConfigHistory  # local import avoids circularity

    row = (
        RecurrentHabitConfigHistory.objects
        .filter(habit=habit, effective_from__lte=period_start)
        .order_by('-effective_from')
        .first()
    )
    if row is not None:
        return row.times, row.time_frame

    # Fallback: oldest row (shouldn't occur for properly migrated data)
    oldest = (
        RecurrentHabitConfigHistory.objects
        .filter(habit=habit)
        .order_by('effective_from')
        .first()
    )
    if oldest is not None:
        logger.warning(
            'habit %s has no config row covering period %s — using oldest row (%s)',
            habit.id, period_start, oldest.effective_from,
        )
        return oldest.times, oldest.time_frame

    # Last resort fallback to live values
    logger.warning(
        'habit %s has NO config history at all — falling back to live values',
        habit.id,
    )
    return habit.times, habit.time_frame


# ────────────────────────────────────────────────────────────────────────────
# Streak computation
# ────────────────────────────────────────────────────────────────────────────

def compute_streak_for_habit(
    habit,
    up_to_period_start: datetime.date,
    time_frame_override: str | None = None,
) -> int:
    """
    Walk backwards from `up_to_period_start` through existing XP ledger rows
    for this habit, counting consecutive completed periods.

    A period is "complete" if a UserXPLedger row exists for it. We stop as
    soon as a gap is found.

    `time_frame_override` short-circuits the config-history DB lookup when the
    caller already knows the correct time_frame (e.g. inside reconcile_user_xp
    or _award_xp_core), eliminating an N+1 query per period.

    When not provided, the time_frame is looked up from config history so that
    a W→M change naturally resets the streak (old weekly ledger entries won't
    be found when walking back in monthly steps).
    """
    from Models.habits.models import UserXPLedger  # local import avoids circularity

    awarded_periods = set(
        UserXPLedger.objects
        .filter(habit=habit)
        .values_list('period_start', flat=True)
    )
    # Include the period we are about to award (not in DB yet)
    awarded_periods.add(up_to_period_start)

    # Use caller-supplied time_frame when available to avoid extra DB hit
    if time_frame_override is not None:
        tf = time_frame_override
    else:
        _, tf = _config_for_period(habit, up_to_period_start)

    streak = 0
    cursor = up_to_period_start
    while cursor in awarded_periods:
        streak += 1
        cursor = prev_period_start(cursor, tf)
    return streak


# ────────────────────────────────────────────────────────────────────────────
# Core award logic
# ────────────────────────────────────────────────────────────────────────────

BASE_XP = {'W': 50, 'M': 175}


def _award_xp_core(
    habit,
    period_start: datetime.date,
    times: int,
    time_frame: str,
) -> bool:
    """
    Low-level: check if the period is complete under the given (times,
    time_frame) config and, if so, create a UserXPLedger entry.

    Returns True if XP was newly awarded, False otherwise.
    This is the single source-of-truth for all XP award logic.
    """
    from Models.habits.models import UserXPLedger  # local import

    p_end = period_end_for(period_start, time_frame)

    # Never award XP for a period that hasn't fully closed yet
    if p_end >= datetime.date.today():
        return False

    # Count DONE checkmarks in this period
    done_count = (
        habit.checkmarks
        .filter(date__gte=period_start, date__lte=p_end, status='DONE')
        .count()
    )

    if done_count < times:
        logger.debug(
            'habit %s period %s: %d/%d done — no XP',
            habit.id, period_start, done_count, times,
        )
        return False

    # Already awarded?
    if UserXPLedger.objects.filter(habit=habit, period_start=period_start).exists():
        logger.debug('XP already awarded for habit %s period %s', habit.id, period_start)
        return False

    # Pass time_frame directly to avoid a redundant config-history DB lookup
    streak  = compute_streak_for_habit(habit, period_start, time_frame_override=time_frame)
    multi   = streak_multiplier(streak)
    base    = BASE_XP[time_frame]
    awarded = int(base * multi)
    reason  = 'WEEKLY_HABIT' if time_frame == 'W' else 'MONTHLY_HABIT'

    UserXPLedger.objects.create(
        user             = habit.owner,
        habit            = habit,
        habit_title_snap = habit.title,
        period_start     = period_start,
        xp_awarded       = awarded,
        streak_at_award  = streak,
        multiplier       = multi,
        reason           = reason,
    )
    logger.info(
        'Awarded %d XP to user %s for habit "%s" (period %s, streak %d, ×%s)',
        awarded, habit.owner_id, habit.title, period_start, streak, multi,
    )
    return True


def try_award_xp_for_period(habit, period_start: datetime.date) -> bool:
    """
    Check if the given habit's period (identified by period_start) is fully
    completed and, if so, create a UserXPLedger entry.

    Returns True if XP was newly awarded, False otherwise (already awarded or
    period not complete).

    This function is idempotent — calling it twice for the same
    (habit, period_start) is safe due to the DB unique constraint.

    The (times, time_frame) used for evaluation are looked up from
    RecurrentHabitConfigHistory so that changes to the live habit config
    do not affect evaluation of past periods.
    """
    from Models.habits.models import RecurrentHabit  # local import

    # Only RecurrentHabits earn periodic XP for now
    if not isinstance(habit, RecurrentHabit):
        return False

    times, time_frame = _config_for_period(habit, period_start)
    return _award_xp_core(habit, period_start, times, time_frame)


def try_award_xp_for_checkmark(checkmark) -> bool:
    """
    Entry point called from the CheckMark post_save signal.
    Determines which period the checkmark belongs to and attempts to award XP.
    Only triggers on a *closed* period (the period has fully ended today or earlier).
    """
    from Models.habits.models import RecurrentHabit  # local import

    habit = checkmark.habit
    try:
        habit = RecurrentHabit.objects.get(pk=habit.pk)
    except RecurrentHabit.DoesNotExist:
        return False  # Goals don't earn periodic XP yet

    today = datetime.date.today()

    # Look up the historically-correct config for this checkmark's date
    times, time_frame = _config_for_period(habit, checkmark.date)
    p_start = period_start_for(checkmark.date, time_frame)
    p_end   = period_end_for(p_start, time_frame)

    # Only award once the period has fully closed
    if p_end >= today:
        return False

    return _award_xp_core(habit, p_start, times, time_frame)


# ────────────────────────────────────────────────────────────────────────────
# Settle un-awarded past periods before a config change
# ────────────────────────────────────────────────────────────────────────────

def settle_habit_xp_before_config_change(
    habit,
    old_times: int,
    old_time_frame: str,
) -> int:
    """
    Called immediately before saving a config change (times or time_frame)
    on a RecurrentHabit.

    Scans all closed periods governed by (old_times, old_time_frame) and
    awards any XP that hasn't been recorded yet using the OLD config.

    This guarantees that once the new config takes effect, no past period
    will ever be re-evaluated under the new rules.

    Returns the number of newly awarded entries.
    """
    from Models.habits.models import RecurrentHabitConfigHistory  # local import

    today         = datetime.date.today()
    awarded_count = 0

    # Find when this old config *most recently* became effective.
    # Using the most-recent row is important when a config value has cycled
    # (e.g. 3→1→3): we only want to settle from the start of the latest
    # window with these values, not from the very first time they appeared.
    old_config_row = (
        RecurrentHabitConfigHistory.objects
        .filter(habit=habit, times=old_times, time_frame=old_time_frame)
        .order_by('-effective_from')
        .first()
    )
    if old_config_row:
        range_start = period_start_for(old_config_row.effective_from, old_time_frame)
    else:
        range_start = period_start_for(habit.created_at.date(), old_time_frame)

    cursor = period_start_for(today - datetime.timedelta(days=1), old_time_frame)

    # Collect all closed periods in this config window (newest first is fine for collection)
    periods_to_settle = []
    for _ in range(104):
        if cursor < range_start:
            break
        p_end = period_end_for(cursor, old_time_frame)
        if p_end < today:
            periods_to_settle.append(cursor)
        cursor = prev_period_start(cursor, old_time_frame)

    # Award oldest → newest so streak counts accumulate correctly.
    # (Streak computation reads already-written ledger rows, so order matters.)
    for period_start in reversed(periods_to_settle):
        if _award_xp_core(habit, period_start, old_times, old_time_frame):
            awarded_count += 1

    return awarded_count


# ────────────────────────────────────────────────────────────────────────────
# Reconcile all missing past periods for a user (called from API on profile load)
# ────────────────────────────────────────────────────────────────────────────

def reconcile_user_xp(user) -> int:
    """
    Scan all closed periods across all of the user's RecurrentHabits and award
    any XP that was missed.

    Each period is evaluated under the config that was in effect at that
    period_start (via RecurrentHabitConfigHistory), so changing times or
    time_frame never retroactively affects previously un-awarded periods.

    Returns the number of newly awarded entries.
    """
    from Models.habits.models import RecurrentHabit  # local import

    today         = datetime.date.today()
    awarded_count = 0

    habits = RecurrentHabit.objects.filter(owner=user).prefetch_related('config_history')
    for habit in habits:
        # Walk config history windows in chronological order
        config_rows = list(habit.config_history.order_by('effective_from'))
        if not config_rows:
            continue

        for i, cfg in enumerate(config_rows):
            tf        = cfg.time_frame
            times     = cfg.times
            cfg_start = period_start_for(cfg.effective_from, tf)

            # Upper bound: either the next config's effective_from, or today
            if i + 1 < len(config_rows):
                cfg_end_excl = config_rows[i + 1].effective_from
            else:
                cfg_end_excl = today

            # Start cursor at last closed period within this config window
            window_end_date = min(
                today - datetime.timedelta(days=1),
                cfg_end_excl - datetime.timedelta(days=1),
            )
            cursor = period_start_for(window_end_date, tf)

            # cursor is already capped to cfg_end_excl - 1 day above, so it
            # can never start inside the *next* config's window — no skip
            # condition needed inside the loop.
            periods_to_award = []
            for _ in range(104):
                if cursor < cfg_start:
                    break
                p_end = period_end_for(cursor, tf)
                if p_end < today:
                    periods_to_award.append(cursor)
                cursor = prev_period_start(cursor, tf)

            # Award oldest → newest so streak counts accumulate correctly.
            for period_start in reversed(periods_to_award):
                if _award_xp_core(habit, period_start, times, tf):
                    awarded_count += 1

    return awarded_count
