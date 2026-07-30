from typing import Optional
from django.db.models import QuerySet
from apps.settings.models import TenantSetting, GlobalSetting


def get_tenant_setting_queryset(
    organization_id: int | None = None,
    **kwargs,
) -> QuerySet[TenantSetting]:
    """Alias for API viewset compatibility."""
    qs = TenantSetting.objects.all()
    if organization_id:
        qs = qs.filter(organization_id=organization_id)
    return qs


def get_global_setting_queryset(**kwargs) -> QuerySet[GlobalSetting]:
    """Alias for API viewset compatibility."""
    return GlobalSetting.objects.all()


def get_tenant_settings(
    organization_id: int,
    *,
    environment: Optional[str] = None,
) -> QuerySet[TenantSetting]:
    """Return all settings for a tenant (organization).

    Args:
        organization_id: Primary key of the organization.
        environment: Optionally filter by environment (defaults to all).

    Returns:
        QuerySet of TenantSetting objects.
    """
    qs = TenantSetting.objects.filter(organization_id=organization_id)
    if environment:
        qs = qs.filter(environment=environment)
    return qs


def get_global_settings() -> QuerySet[GlobalSetting]:
    """Return all global settings.

    Returns:
        QuerySet of GlobalSetting objects.
    """
    return GlobalSetting.objects.all()


def get_setting_by_key(key: str, *, environment: str = "production") -> Optional[GlobalSetting]:
    """Return a global setting by its key, or None.

    Args:
        key: The setting key to look up.
        environment: Unused; kept for API compatibility.

    Returns:
        GlobalSetting instance or None.
    """
    return GlobalSetting.objects.filter(key=key).first()
