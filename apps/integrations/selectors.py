"""Selectors for integrations app."""

from typing import Optional
from django.db.models import QuerySet
from apps.integrations.models import Integration, IntegrationLog


def get_integrations(
    organization_id: Optional[int] = None,
    *,
    integration_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> QuerySet[Integration]:
    """Return integrations with optional filters.

    Args:
        organization_id: Filter by organization.
        integration_type: Filter by integration type.
        status: Filter by status (e.g. 'active', 'inactive').
        search: Search by integration name (case-insensitive).

    Returns:
        QuerySet of Integration objects.
    """
    qs = Integration.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if integration_type:
        qs = qs.filter(integration_type=integration_type)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(name__icontains=search)
    return qs


def get_org_integrations(organization_id: int) -> QuerySet[Integration]:
    """Return all integrations for a specific organization.

    Args:
        organization_id: Primary key of the organization.

    Returns:
        QuerySet of Integration objects belonging to the organization.
    """
    return Integration.objects.filter(organization_id=organization_id).select_related("organization")


# --- Existing queryset-based selectors preserved below ---

def get_integration_queryset(
    *,
    organization_id: Optional[int] = None,
    integration_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> QuerySet[Integration]:
    """Get integrations queryset for API views."""
    queryset = Integration.objects.select_related("organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if integration_type:
        queryset = queryset.filter(integration_type=integration_type)

    if status:
        queryset = queryset.filter(status=status)

    if search:
        queryset = queryset.filter(name__icontains=search)

    return queryset


def get_integration_log_queryset(
    *,
    integration_id: Optional[int] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
) -> QuerySet[IntegrationLog]:
    """Get integration logs queryset for API views."""
    queryset = IntegrationLog.objects.select_related("integration")

    if integration_id is not None:
        queryset = queryset.filter(integration_id=integration_id)

    if action:
        queryset = queryset.filter(action=action)

    if status:
        queryset = queryset.filter(status=status)

    return queryset
