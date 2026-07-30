"""Selectors for analytics app."""

from typing import Optional
from django.db.models import QuerySet, Sum
from apps.analytics.models import AnalyticsEvent, AnalyticsAggregation


def get_events(
    organization_id: Optional[int] = None,
    *,
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    module: Optional[str] = None,
) -> QuerySet[AnalyticsEvent]:
    """Return analytics events with optional filters.

    Args:
        organization_id: Filter by organization.
        user_id: Filter by user.
        event_type: Filter by event type.
        module: Filter by module name.

    Returns:
        QuerySet of AnalyticsEvent objects.
    """
    qs = AnalyticsEvent.objects.select_related("organization", "user")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if user_id is not None:
        qs = qs.filter(user_id=user_id)
    if event_type:
        qs = qs.filter(event_type=event_type)
    if module:
        qs = qs.filter(module=module)
    return qs


def get_aggregations(
    organization_id: Optional[int] = None,
    *,
    module: Optional[str] = None,
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
) -> QuerySet[AnalyticsAggregation]:
    """Return analytics aggregations with optional filters.

    Args:
        organization_id: Filter by organization.
        module: Filter by module name.
        period_from: Filter by period start date (inclusive).
        period_to: Filter by period end date (inclusive).

    Returns:
        QuerySet of AnalyticsAggregation objects.
    """
    qs = AnalyticsAggregation.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if module:
        qs = qs.filter(module=module)
    if period_from:
        qs = qs.filter(period__gte=period_from)
    if period_to:
        qs = qs.filter(period__lte=period_to)
    return qs


def get_org_metrics(organization_id: int, module: Optional[str] = None) -> QuerySet[AnalyticsAggregation]:
    """Return aggregated metrics for a specific organization.

    Args:
        organization_id: Primary key of the organization.
        module: Optionally filter by module name.

    Returns:
        QuerySet of AnalyticsAggregation objects for the organization.
    """
    qs = AnalyticsAggregation.objects.filter(organization_id=organization_id)
    if module:
        qs = qs.filter(module=module)
    return qs.order_by("period", "module", "metric")


# --- Existing queryset-based selectors preserved below ---

def get_analytics_event_queryset(
    *,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    module: Optional[str] = None,
) -> QuerySet[AnalyticsEvent]:
    """Get analytics events queryset for API views."""
    queryset = AnalyticsEvent.objects.select_related("organization", "user")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if event_type:
        queryset = queryset.filter(event_type=event_type)

    if module:
        queryset = queryset.filter(module=module)

    return queryset


def get_analytics_aggregation_queryset(
    *,
    organization_id: Optional[int] = None,
    module: Optional[str] = None,
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
) -> QuerySet[AnalyticsAggregation]:
    """Get analytics aggregations queryset for API views."""
    queryset = AnalyticsAggregation.objects.select_related("organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if module:
        queryset = queryset.filter(module=module)

    if period_from:
        queryset = queryset.filter(period__gte=period_from)

    if period_to:
        queryset = queryset.filter(period__lte=period_to)

    return queryset
