"""Selectors for webhooks app."""

from typing import Optional
from django.db.models import QuerySet
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery


def get_webhook_endpoints(
    organization_id: Optional[int] = None,
    *,
    is_active: Optional[bool] = None,
    event_type: Optional[str] = None,
) -> QuerySet[WebhookEndpoint]:
    """Return webhook endpoints with optional filters.

    Args:
        organization_id: Filter by organization.
        is_active: Filter by active status.
        event_type: Filter by subscribed event type.

    Returns:
        QuerySet of WebhookEndpoint objects.
    """
    qs = WebhookEndpoint.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if event_type:
        qs = qs.filter(events__contains=[event_type])
    return qs


def get_webhook_deliveries(
    *,
    endpoint_id: Optional[int] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
) -> QuerySet[WebhookDelivery]:
    """Return webhook delivery records with optional filters.

    Args:
        endpoint_id: Filter by endpoint.
        event_type: Filter by event type.
        status: Filter by delivery status.

    Returns:
        QuerySet of WebhookDelivery objects.
    """
    qs = WebhookDelivery.objects.select_related("endpoint")
    if endpoint_id is not None:
        qs = qs.filter(endpoint_id=endpoint_id)
    if event_type is not None:
        qs = qs.filter(event_type=event_type)
    if status is not None:
        qs = qs.filter(status=status)
    return qs


def get_org_webhooks(organization_id: int) -> QuerySet[WebhookEndpoint]:
    """Return all webhook endpoints for a specific organization.

    Args:
        organization_id: Primary key of the organization.

    Returns:
        QuerySet of WebhookEndpoint objects belonging to the organization.
    """
    return WebhookEndpoint.objects.filter(organization_id=organization_id)


# --- Existing queryset-based selectors preserved below ---

def get_webhook_endpoint_queryset(
    *,
    organization_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    event_type: Optional[str] = None,
) -> QuerySet[WebhookEndpoint]:
    """Get webhook endpoints queryset for API views."""
    queryset = WebhookEndpoint.objects.select_related("organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if event_type:
        queryset = queryset.filter(events__contains=[event_type])

    return queryset


def get_webhook_delivery_queryset(
    *,
    endpoint_id: Optional[int] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
) -> QuerySet[WebhookDelivery]:
    """Get webhook deliveries queryset for API views."""
    queryset = WebhookDelivery.objects.select_related("endpoint")

    if endpoint_id is not None:
        queryset = queryset.filter(endpoint_id=endpoint_id)

    if event_type is not None:
        queryset = queryset.filter(event_type=event_type)

    if status is not None:
        queryset = queryset.filter(status=status)

    return queryset
