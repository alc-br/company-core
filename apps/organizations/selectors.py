from typing import Optional
from django.db.models import QuerySet
from apps.organizations.models import Organization, Membership, Invitation
from apps.common.constants import MembershipStatus, InvitationStatus


def get_organization_by_id(
    organization_id: int,
    *,
    select_related: tuple = ("owner",),
) -> Organization:
    """Get a single organization by ID with optimized queryset."""
    return Organization.objects.select_related(*select_related).get(id=organization_id)


def get_organization_by_slug(slug: str) -> Organization:
    """Get a single organization by slug."""
    return Organization.objects.select_related("owner").get(slug=slug)


def get_user_organizations(
    user_id: int,
    *,
    role: Optional[int] = None,
    status: int = MembershipStatus.ACTIVE,
) -> QuerySet[Organization]:
    """Get all organizations for a user."""
    queryset = Organization.objects.filter(
        memberships__user_id=user_id,
        memberships__status=status,
    ).select_related("owner").distinct()

    if role is not None:
        queryset = queryset.filter(memberships__role=role)

    return queryset


def get_organization_members(
    organization_id: int,
    *,
    role: Optional[int] = None,
    status: int = MembershipStatus.ACTIVE,
    limit: int = 100,
    offset: int = 0,
) -> QuerySet[Membership]:
    """Get members of an organization with pagination."""
    queryset = Membership.objects.filter(
        organization_id=organization_id,
        status=status,
    ).select_related("user", "invited_by")

    if role is not None:
        queryset = queryset.filter(role=role)

    return queryset[offset:offset + limit]


def get_pending_invitations(
    organization_id: int,
    *,
    limit: int = 100,
) -> QuerySet[Invitation]:
    """Get pending invitations for an organization."""
    return Invitation.objects.filter(
        organization_id=organization_id,
        status=InvitationStatus.PENDING,
    ).select_related("invited_by")[:limit]


def check_user_is_member(user_id: int, organization_id: int) -> bool:
    """Check if a user is an active member of an organization."""
    return Membership.objects.filter(
        user_id=user_id,
        organization_id=organization_id,
        status=MembershipStatus.ACTIVE,
    ).exists()


def get_user_role(user_id: int, organization_id: int) -> Optional[int]:
    """Get the role of a user in an organization."""
    membership = Membership.objects.filter(
        user_id=user_id,
        organization_id=organization_id,
        status=MembershipStatus.ACTIVE,
    ).first()
    return membership.role if membership else None
