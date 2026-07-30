from typing import Optional
from django.db.models import QuerySet
from apps.audit.models import AuditLog


def get_audit_log_queryset(
    *,
    organization_id: Optional[int] = None,
    actor_id: Optional[int] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
) -> QuerySet[AuditLog]:
    """Get audit log queryset for API views."""
    queryset = AuditLog.objects.select_related("actor", "organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if actor_id is not None:
        queryset = queryset.filter(actor_id=actor_id)

    if action is not None:
        queryset = queryset.filter(action=action)

    if target_type is not None:
        queryset = queryset.filter(target_type=target_type)

    if target_id is not None:
        queryset = queryset.filter(target_id=target_id)

    return queryset
