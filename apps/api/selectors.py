from typing import Optional
from django.db.models import QuerySet
from apps.api.models import APIKey, PersonalAccessToken, ServiceAccount


def get_api_keys(
    organization_id: Optional[int] = None,
    *,
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> QuerySet[APIKey]:
    """Return API keys with optional filters.

    Args:
        organization_id: Filter by organization.
        user_id: Filter by owning user.
        is_active: Filter by active status.

    Returns:
        QuerySet of APIKey objects.
    """
    qs = APIKey.objects.select_related("user", "organization", "created_by")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if user_id is not None:
        qs = qs.filter(user_id=user_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs


def get_service_accounts(
    organization_id: Optional[int] = None,
    *,
    is_active: Optional[bool] = None,
) -> QuerySet[ServiceAccount]:
    """Return service accounts with optional filters.

    Args:
        organization_id: Filter by organization.
        is_active: Filter by active status.

    Returns:
        QuerySet of ServiceAccount objects.
    """
    qs = ServiceAccount.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs


def get_active_tokens(user_id: int) -> QuerySet[PersonalAccessToken]:
    """Return active personal access tokens for a user.

    A token is considered active if it has no expiration date or the expiration
    date is in the future.

    Args:
        user_id: Primary key of the user.

    Returns:
        QuerySet of active PersonalAccessToken objects.
    """
    from django.utils import timezone
    return (
        PersonalAccessToken.objects
        .filter(user_id=user_id)
        .filter(expires_at__isnull=True) | PersonalAccessToken.objects.filter(user_id=user_id, expires_at__gt=timezone.now())
    )
