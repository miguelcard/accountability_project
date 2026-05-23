"""
Management command: fix_config_history

Repairs config-history rows that were corrupted by the old backdating logic.

Old behaviour (bug):
  When a times-only change was made after a time_frame change in the same
  period, the code created a new row backdated to period_start.  The
  existing "today" row (from the time_frame change) then silently overrode
  it, leaving the habit stuck at the old times value.

What this command does for each RecurrentHabit:
  1. Determines the current-period start (based on the habit's live time_frame).
  2. Within that period, finds ALL config-history rows.
  3. Keeps the most-recent one and updates it to match the habit's live
     times / time_frame (the source of truth stored on the model).
  4. Deletes every other row in the same period (they are superseded).

Run with --dry-run to preview changes without writing anything.
"""

import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from Models.habits.models import RecurrentHabit, RecurrentHabitConfigHistory
from Models.habits.xp_utils import period_start_for


class Command(BaseCommand):
    help = 'Fix corrupted config-history rows caused by the old backdating logic.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be changed without modifying the database.',
        )
        parser.add_argument(
            '--habit-id',
            type=int,
            default=None,
            help='Restrict repair to a single habit by ID.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        habit_id_filter = options['habit_id']
        today = timezone.now().date()

        habits_qs = RecurrentHabit.objects.prefetch_related('config_history')
        if habit_id_filter:
            habits_qs = habits_qs.filter(pk=habit_id_filter)

        fixed = 0
        for habit in habits_qs:
            period_start = period_start_for(today, habit.time_frame)

            entries_in_period = list(
                RecurrentHabitConfigHistory.objects
                .filter(habit=habit, effective_from__gte=period_start, effective_from__lte=today)
                .order_by('-effective_from')
            )

            if not entries_in_period:
                continue  # nothing to repair in this period

            most_recent = entries_in_period[0]
            stale_entries = entries_in_period[1:]  # older ones within the same period

            needs_update = (
                most_recent.times != habit.times
                or most_recent.time_frame != habit.time_frame
            )
            needs_delete = len(stale_entries) > 0

            if not needs_update and not needs_delete:
                continue

            self.stdout.write(
                f'Habit {habit.id} ("{habit.title}"): '
                f'most-recent entry {most_recent.effective_from} '
                f'{most_recent.times}x/{most_recent.time_frame} '
                f'→ {habit.times}x/{habit.time_frame}; '
                f'deleting {len(stale_entries)} stale entr{"y" if len(stale_entries)==1 else "ies"}: '
                f'{[str(e.effective_from) for e in stale_entries]}'
            )

            if not dry_run:
                if needs_update:
                    most_recent.times = habit.times
                    most_recent.time_frame = habit.time_frame
                    most_recent.save(update_fields=['times', 'time_frame'])

                if needs_delete:
                    stale_ids = [e.pk for e in stale_entries]
                    RecurrentHabitConfigHistory.objects.filter(pk__in=stale_ids).delete()

            fixed += 1

        suffix = ' (dry run)' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'Done{suffix}. {fixed} habit(s) repaired.'
        ))
