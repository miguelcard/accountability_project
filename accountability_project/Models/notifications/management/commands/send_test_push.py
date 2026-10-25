"""
Management command: send_test_push

Sends a test push notification straight through FCM to every registered device of one user
and prints the outcome per device. Unlike notify_user(), errors are shown instead of only
logged, so it can be used to verify device registration and the service account's FCM
permissions without going through a real event (e.g. adding someone to a space).

Does not modify any data (invalid tokens are reported, not deleted).

Usage:
    python manage.py send_test_push <username-or-email>
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from firebase_admin import messaging

from Models.notifications.models import DeviceToken
from Models.users.models import User


class Command(BaseCommand):
    help = 'Send a test push notification to all registered devices of a user and report the result.'

    def add_arguments(self, parser):
        parser.add_argument('user', help='Username or email of the recipient.')
        parser.add_argument('--title', default='Test notification')
        parser.add_argument('--body', default='If you can read this, push notifications work.')

    def handle(self, *args, **options):
        identifier = options['user']
        user = User.objects.filter(Q(username=identifier.strip().lower()) | Q(email__iexact=identifier.strip())).first()
        if user is None:
            raise CommandError(f'No user found with username or email "{identifier}".')

        tokens = list(DeviceToken.objects.filter(user=user).order_by('id'))
        if not tokens:
            raise CommandError(
                f'User "{user.username}" has no registered devices. Open the app on the phone while '
                'logged in as this (non-anonymous) user and accept the notification permission.'
            )

        failures = 0
        for device in tokens:
            label = f'{device.platform} device (token ...{device.token[-6:]})'
            message = messaging.Message(
                notification=messaging.Notification(title=options['title'], body=options['body']),
                data={'type': 'test'},
                token=device.token,
            )
            try:
                messaging.send(message)
                self.stdout.write(self.style.SUCCESS(f'OK     {label}'))
            except messaging.UnregisteredError:
                failures += 1
                self.stdout.write(self.style.WARNING(f'STALE  {label}: token no longer valid (app reinstalled?)'))
            except Exception as error:
                failures += 1
                self.stdout.write(self.style.ERROR(f'FAILED {label}: {type(error).__name__}: {error}'))

        self.stdout.write(f'{len(tokens) - failures}/{len(tokens)} sent to "{user.username}".')
        if failures:
            raise CommandError('Some sends failed, see above.')
