import logging

from firebase_admin import messaging

from Models.notifications.models import DeviceToken

logger = logging.getLogger(__name__)


def notify_user(recipient, title, body, data=None):
    """
    Send a push notification to every registered device of `recipient` via FCM.

    Never raises: delivery problems are logged so they cannot fail the calling request.
    Tokens that FCM reports as invalid/unregistered are deleted.
    """
    try:
        tokens = list(DeviceToken.objects.filter(user=recipient).order_by('id').values_list('token', flat=True))
        if not tokens:
            return

        payload = {str(k): str(v) for k, v in (data or {}).items()}
        for token in tokens:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=payload,
                token=token,
            )
            try:
                messaging.send(message)
            except (messaging.UnregisteredError, messaging.SenderIdMismatchError):
                DeviceToken.objects.filter(token=token).delete()
                logger.info("Removed unregistered device token for user=%s", recipient.pk)
            except Exception:
                logger.exception("Failed to send push to a device of user=%s", recipient.pk)
    except Exception:
        logger.exception("notify_user failed for user=%s", getattr(recipient, 'pk', None))
