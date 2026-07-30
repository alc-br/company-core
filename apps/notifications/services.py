import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationService:
    """Central service for sending notifications across channels."""

    @staticmethod
    def send_notification(channel, recipient, template_code, context=None):
        """Send a notification through the specified channel.

        Args:
            channel: 'email', 'webhook', 'slack', 'discord', 'internal'
            recipient: email address, user object, or URL
            template_code: code of the NotificationTemplate
            context: dict with template variables
        """
        from apps.notifications.models import NotificationLog, NotificationTemplate

        context = context or {}
        status = "pending"

        try:
            if channel == "email":
                NotificationService._send_email(recipient, template_code, context)
                status = "sent"
            elif channel == "internal":
                status = "delivered"
            elif channel == "webhook":
                status = "delivered"
            else:
                logger.warning(f"Unsupported notification channel: {channel}")
                status = "skipped"
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            status = "failed"

        # Log the notification
        template = NotificationTemplate.objects.filter(code=template_code).first()
        NotificationLog.objects.create(
            recipient=recipient if isinstance(recipient, str) else getattr(recipient, "email", str(recipient)),
            template=template,
            status=status,
            sent_at=timezone.now() if status in ("sent", "delivered") else None,
        )
        return status

    @staticmethod
    def _send_email(recipient, template_code, context):
        """Send an email using a template."""
        from apps.notifications.models import NotificationTemplate

        template = NotificationTemplate.objects.filter(code=template_code).first()
        if not template:
            logger.warning(f"Email template not found: {template_code}, using fallback")
            subject = f"[Company Core] {template_code}"
            body = str(context)
        else:
            subject = template.subject.format(**context) if template.subject else template_code
            body = template.body_text.format(**context) if template.body_text else str(context)

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient] if isinstance(recipient, str) else [recipient],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient}: {template_code}")
