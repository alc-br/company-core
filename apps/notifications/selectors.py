from typing import Optional
from django.db.models import QuerySet
from apps.notifications.models import NotificationChannel, NotificationLog, NotificationTemplate


def get_notification_channels(
    organization_id: Optional[int] = None,
    *,
    is_active: Optional[bool] = None,
    channel_type: Optional[int] = None,
) -> QuerySet[NotificationChannel]:
    """Return notification channels with optional filters.

    Args:
        organization_id: Filter by organization.
        is_active: Filter by active status.
        channel_type: Filter by channel type (integer from NotificationChannelType).

    Returns:
        QuerySet of NotificationChannel objects.
    """
    qs = NotificationChannel.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if channel_type is not None:
        qs = qs.filter(type=channel_type)
    return qs


def get_notification_logs(
    *,
    channel_id: Optional[int] = None,
    status: Optional[str] = None,
    recipient: Optional[str] = None,
    limit: int = 100,
) -> QuerySet[NotificationLog]:
    """Return notification logs with optional filters.

    Args:
        channel_id: Filter by channel.
        status: Filter by delivery status.
        recipient: Filter by recipient email.
        limit: Maximum number of results.

    Returns:
        QuerySet of NotificationLog objects.
    """
    qs = NotificationLog.objects.select_related("channel", "template")
    if channel_id is not None:
        qs = qs.filter(channel_id=channel_id)
    if status:
        qs = qs.filter(status=status)
    if recipient:
        qs = qs.filter(recipient=recipient)
    return qs[:limit]


def get_notification_logs_for_org(organization_id: int, *, limit: int = 100) -> QuerySet[NotificationLog]:
    """Return notification logs for a specific organization.

    Args:
        organization_id: Primary key of the organization.
        limit: Maximum number of results.

    Returns:
        QuerySet of NotificationLog objects associated with the organization's channels.
    """
    return (
        NotificationLog.objects
        .filter(channel__organization_id=organization_id)
        .select_related("channel", "template")
        .order_by("-created_at")[:limit]
    )


def get_notification_channel_queryset(**kwargs) -> QuerySet[NotificationChannel]:
    """ViewSet-compatible queryset for NotificationChannel."""
    return get_notification_channels(**kwargs)


def get_notification_template_queryset(**kwargs) -> QuerySet[NotificationTemplate]:
    """ViewSet-compatible queryset for NotificationTemplate."""
    return get_templates(**kwargs)


def get_notification_log_queryset(**kwargs) -> QuerySet[NotificationLog]:
    """ViewSet-compatible queryset for NotificationLog."""
    return get_notification_logs(**kwargs)


def get_templates(
    *,
    channel: Optional[str] = None,
) -> QuerySet[NotificationTemplate]:
    """Return notification templates, optionally filtered by channel.

    Args:
        channel: Filter by channel name (e.g. 'email', 'sms').

    Returns:
        QuerySet of NotificationTemplate objects.
    """
    qs = NotificationTemplate.objects.all()
    if channel:
        qs = qs.filter(channel=channel)
    return qs
