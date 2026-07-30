from typing import Optional
from django.db.models import Q, QuerySet
from django.conf import settings
from apps.users.models import CustomUser


def get_user_queryset(
    *,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_staff: Optional[bool] = None,
) -> QuerySet[CustomUser]:
    """Get users queryset for API views."""
    queryset = CustomUser.objects.all()

    if search is not None:
        queryset = queryset.filter(
            Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if is_staff is not None:
        queryset = queryset.filter(is_staff=is_staff)

    return queryset


def get_user_by_id(user_id: int) -> CustomUser:
    """Get a single user by ID.

    Args:
        user_id: Primary key of the user.

    Returns:
        The CustomUser instance.

    Raises:
        CustomUser.DoesNotExist: If no user with the given ID exists.
    """
    return CustomUser.objects.get(id=user_id)


def get_user_by_email(email: str) -> CustomUser:
    """Get a single user by email address.

    Args:
        email: The email address to look up.

    Returns:
        The CustomUser instance.

    Raises:
        CustomUser.DoesNotExist: If no user with the given email exists.
    """
    return CustomUser.objects.get(email=email)


def get_users_by_organization(organization_id: int) -> QuerySet[CustomUser]:
    """Return all users that are active members of a given organization.

    Args:
        organization_id: Primary key of the organization.

    Returns:
        QuerySet of CustomUser objects belonging to the organization.
    """
    from apps.organizations.models import Membership
    from apps.common.constants import MembershipStatus

    return CustomUser.objects.filter(
        memberships__organization_id=organization_id,
        memberships__status=MembershipStatus.ACTIVE,
    ).distinct()


def get_tenant_users_queryset(
    organization_id: int,
    *,
    search: Optional[str] = None,
    status: Optional[int] = None,
) -> QuerySet[CustomUser]:
    """Get users that are members of an organization."""
    from apps.organizations.models import Membership
    from apps.common.constants import MembershipStatus

    queryset = CustomUser.objects.filter(
        memberships__organization_id=organization_id,
        memberships__status=status or MembershipStatus.ACTIVE,
    ).distinct()

    if search is not None:
        queryset = queryset.filter(
            Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )

    return queryset
