"""
Management command: cleanup_expired_invites

Deletes PendingInvite rows that were never accepted and expired more than
--older-than-days ago (default: 30).

The retention window keeps recently expired rows so that invite links clicked
shortly after expiry still get "This invite has expired." instead of a
generic "not found". Accepted invites are never deleted by this command.

Intended to run once per day. Safe to run repeatedly.
Use --dry-run to preview the number of rows that would be deleted.
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from Models.spaces.models import PendingInvite

logger = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = 30


class Command(BaseCommand):
    help = (
        'Delete unaccepted PendingInvite rows that expired more than '
        f'--older-than-days days ago (default: {DEFAULT_RETENTION_DAYS}).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--older-than-days',
            type=int,
            default=DEFAULT_RETENTION_DAYS,
            help=(
                'Only delete invites that expired more than this many days ago '
                '(default: %(default)s). Use 0 to delete everything already expired.'
            ),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report how many invites would be deleted without modifying the database.',
        )

    def handle(self, *args, **options):
        older_than_days = options['older_than_days']
        dry_run = options['dry_run']

        if older_than_days < 0:
            raise CommandError('--older-than-days must be 0 or greater.')

        cutoff = timezone.now() - timedelta(days=older_than_days)
        stale_invites = PendingInvite.objects.filter(accepted=False, expires_at__lt=cutoff)

        if dry_run:
            count = stale_invites.count()
            self.stdout.write(self.style.WARNING(
                f'Dry run: {count} expired pending invite(s) would be deleted.'
            ))
            return

        deleted_count, _ = stale_invites.delete()
        logger.info(
            'cleanup_expired_invites deleted %d pending invite(s) that expired before %s '
            '(older_than_days=%d)',
            deleted_count, cutoff.isoformat(), older_than_days,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {deleted_count} expired pending invite(s).'
        ))