import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from Models.users.models import User
from Models.habits.models import UserXPLedger

# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_user(username: str = 'testuser_xpstats') -> User:
    return User.objects.create(
        username=username,
        email=f'{username}@test.com',
        firebase_uid=f'uid_{username}',
    )


def add_ledger_row(
    user: User,
    reason: str,
    streak_at_award: int,
    period_start: datetime.date | None = None,
    xp_awarded: int = 50,
) -> UserXPLedger:
    """Directly insert a ledger row, bypassing XP-award logic."""
    if period_start is None:
        period_start = datetime.date(2026, 1, 6)  # arbitrary past Monday
    return UserXPLedger.objects.create(
        user=user,
        habit=None,
        habit_title_snap='Test Habit',
        period_start=period_start,
        xp_awarded=xp_awarded,
        streak_at_award=streak_at_award,
        multiplier='1.0',
        reason=reason,
    )


def call_xp_stats(user: User) -> dict:
    """Call GET /api/v1/user/xp-stats/ as *user* and return the parsed response data."""
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(reverse('user-xp-stats'))
    return response.data


# ─── XPStatsView — longest_streak_unit tests ─────────────────────────────────

class XPStatsLongestStreakUnitTests(TestCase):
    """
    Covers all five cases for the longest_streak_unit field returned by
    GET /api/v1/user/xp-stats/.

    Each test directly inserts UserXPLedger rows (bypassing signal/XP logic)
    so the unit under test is exclusively the view's aggregation + unit
    derivation logic.
    """

    def _assert_stats(self, user: User, expected_streak: int, expected_unit: str) -> None:
        data = call_xp_stats(user)
        self.assertEqual(data['longest_streak'], expected_streak)
        self.assertEqual(data['longest_streak_unit'], expected_unit)

    # ── Case 1: empty ledger (new user) ──────────────────────────────────────

    def test_empty_ledger_defaults_to_weekly(self):
        """A brand-new user with no XP rows should get streak=0 and unit='W'."""
        user = make_user('xp_empty')
        self._assert_stats(user, expected_streak=0, expected_unit='W')

    # ── Case 2: only weekly habits ────────────────────────────────────────────

    def test_only_weekly_habits_returns_W(self):
        """All WEEKLY_HABIT rows → unit must be 'W'."""
        user = make_user('xp_weekly_only')
        add_ledger_row(user, reason='WEEKLY_HABIT', streak_at_award=3, period_start=datetime.date(2026, 1, 6))
        add_ledger_row(user, reason='WEEKLY_HABIT', streak_at_award=8, period_start=datetime.date(2026, 1, 13))
        add_ledger_row(user, reason='WEEKLY_HABIT', streak_at_award=5, period_start=datetime.date(2026, 1, 20))
        self._assert_stats(user, expected_streak=8, expected_unit='W')

    # ── Case 3: only monthly habits ───────────────────────────────────────────

    def test_only_monthly_habits_returns_M(self):
        """All MONTHLY_HABIT rows → unit must be 'M'."""
        user = make_user('xp_monthly_only')
        add_ledger_row(user, reason='MONTHLY_HABIT', streak_at_award=2, period_start=datetime.date(2026, 1, 1))
        add_ledger_row(user, reason='MONTHLY_HABIT', streak_at_award=3, period_start=datetime.date(2026, 2, 1))
        self._assert_stats(user, expected_streak=3, expected_unit='M')

    # ── Case 4: mixed — weekly streak is higher ───────────────────────────────

    def test_mixed_weekly_higher_returns_W(self):
        """Weekly max (8) > monthly max (3) → longest streak is 8w."""
        user = make_user('xp_mixed_weekly_wins')
        add_ledger_row(user, reason='WEEKLY_HABIT',  streak_at_award=8, period_start=datetime.date(2026, 1, 6))
        add_ledger_row(user, reason='MONTHLY_HABIT', streak_at_award=3, period_start=datetime.date(2026, 2, 1))
        self._assert_stats(user, expected_streak=8, expected_unit='W')

    # ── Case 5: tie — monthly preferred ──────────────────────────────────────

    def test_tie_prefers_monthly(self):
        """When a weekly and a monthly row share the same max streak, 'M' wins."""
        user = make_user('xp_tie')
        add_ledger_row(user, reason='WEEKLY_HABIT',  streak_at_award=5, period_start=datetime.date(2026, 1, 6))
        add_ledger_row(user, reason='MONTHLY_HABIT', streak_at_award=5, period_start=datetime.date(2026, 2, 1))
        self._assert_stats(user, expected_streak=5, expected_unit='M')