from typing import Optional
from django.db.models import QuerySet
from apps.quotas.models import QuotaDefinition, QuotaAllocation


def get_all_quotas(organization_id):
    """Get all quota allocations for an organization."""
    return QuotaAllocation.objects.filter(
        organization_id=organization_id
    ).select_related("definition")


def get_quota_definitions():
    """Get all quota definitions."""
    return QuotaDefinition.objects.all()


def get_quota_definition_queryset(
    *,
    code: Optional[str] = None,
) -> QuerySet[QuotaDefinition]:
    """Get quota definitions queryset for API views."""
    queryset = QuotaDefinition.objects.all()

    if code is not None:
        queryset = queryset.filter(code=code)

    return queryset


def get_quota_allocation_queryset(
    *,
    organization_id: Optional[int] = None,
    definition_id: Optional[int] = None,
    code: Optional[str] = None,
) -> QuerySet[QuotaAllocation]:
    """Get quota allocations queryset for API views."""
    queryset = QuotaAllocation.objects.select_related("definition", "organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if definition_id is not None:
        queryset = queryset.filter(definition_id=definition_id)

    if code is not None:
        queryset = queryset.filter(definition__code=code)

    return queryset
