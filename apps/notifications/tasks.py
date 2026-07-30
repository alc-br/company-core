import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(self, channel, recipient, template_code, context=None):
    """Async notification delivery."""
    from apps.notifications.services import NotificationService

    try:
        status = NotificationService.send_notification(channel, recipient, template_code, context)
        logger.info(f"Notification sent to {recipient}: {template_code} -> {status}")
        return {"recipient": recipient, "template": template_code, "status": status}
    except Exception as exc:
        logger.error(f"Failed to send notification to {recipient}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def send_bulk_notifications_task(self, channel, recipients, template_code, context=None):
    """Bulk notification delivery."""
    from apps.notifications.services import NotificationService

    if not isinstance(recipients, (list, tuple)):
        recipients = [recipients]

    results = {"total": len(recipients), "sent": 0, "failed": 0}

    for recipient in recipients:
        try:
            status = NotificationService.send_notification(channel, recipient, template_code, context)
            if status in ("sent", "delivered"):
                results["sent"] += 1
            else:
                results["failed"] += 1
        except Exception as exc:
            logger.error(f"Bulk notification failed for {recipient}: {exc}")
            results["failed"] += 1

    logger.info(
        f"Bulk notification complete: {results['sent']}/{results['total']} sent, "
        f"{results['failed']} failed for template {template_code}"
    )
    return results


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_notifications_task(self, days=90):
    """Clean up old notification logs."""
    from apps.notifications.models import NotificationLog
    from django.utils import timezone
    from datetime import timedelta

    try:
        cutoff = timezone.now() - timedelta(days=days)
        count, _ = NotificationLog.objects.filter(created_at__lt=cutoff).delete()
        logger.info(f"Cleaned up {count} old notification logs (older than {days} days)")
        return {"deleted_count": count, "days": days}
    except Exception as exc:
        logger.error(f"Failed to cleanup old notifications: {exc}")
        self.retry(exc=exc)
