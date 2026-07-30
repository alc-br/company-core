"""Selectors for usage app."""

from typing import Optional
from django.db.models import QuerySet, Sum
from apps.usage.models import UsageRecord


def get_usage_records(
    organization_id: Optional[int] = None,
    *,
    user_id: Optional[int] = None,
    metric_type: Optional[int] = None,
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
) -> QuerySet[UsageRecord]:
    """Return usage records with optional filters.

    Args:
        organization_id: Filter by organization.
        user_id: Filter by user.
        metric_type: Filter by metric type (integer from MetricType).
        period_from: Filter by period start date (inclusive).
        period_to: Filter by period end date (inclusive).

    Returns:
        QuerySet of UsageRecord objects.
    """
    qs = UsageRecord.objects.select_related("organization", "user")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if user_id is not None:
        qs = qs.filter(user_id=user_id)
    if metric_type is not None:
        qs = qs.filter(metric_type=metric_type)
    if period_from:
        qs = qs.filter(period__gte=period_from)
    if period_to:
        qs = qs.filter(period__lte=period_to)
    return qs


def get_usage_summary(organization_id: int, *, period_from: Optional[str] = None, period_to: Optional[str] = None):
    """Return aggregated usage summary for an organization.

    Args:
        organization_id: Primary key of the organization.
        period_from: Optional period start date (inclusive).
        period_to: Optional period end date (inclusive).

    Returns:
        QuerySet of UsageRecord objects annotated with total values per metric type.
    """
    qs = UsageRecord.objects.filter(organization_id=organization_id)
    if period_from:
        qs = qs.filter(period__gte=period_from)
    if period_to:
        qs = qs.filter(period__lte=period_to)
    return qs.values("metric_type", "unit").annotate(total=Sum("value")).order_by("metric_type")


# --- Existing queryset-based selectors preserved below ---

def get_usage_record_queryset(
    *,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    metric_type: Optional[int] = None,
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
) -> QuerySet[UsageRecord]:
    """Get usage records queryset for API views."""
    queryset = UsageRecord.objects.select_related("organization", "user")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if metric_type is not None:
        queryset = queryset.filter(metric_type=metric_type)

    if period_from:
        queryset = queryset.filter(period__gte=period_from)

    if period_to:
        queryset = queryset.filter(period__lte=period_to)

    return queryset
