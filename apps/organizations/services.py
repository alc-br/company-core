import logging
from typing import Optional
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.organizations.models import Organization, Membership, Invitation
from apps.common.constants import MembershipRole, MembershipStatus, InvitationStatus
from apps.common.exceptions import NotFoundException, PermissionDeniedError, ValidationError

logger = logging.getLogger(__name__)


class OrganizationService:
    """Service layer for organization operations."""

    @staticmethod
    @transaction.atomic
    def create_organization(name: str, owner, slug: Optional[str] = None) -> Organization:
        """Create a new organization with the given owner."""
        organization = Organization.objects.create(
            name=name,
            slug=slug or name.lower().replace(" ", "-"),
            owner=owner,
            status=MembershipStatus.ACTIVE,
        )

        Membership.objects.create(
            user=owner,
            organization=organization,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
            invited_by=owner,
        )

        logger.info(f"Organization '{name}' created by user {owner.id}")
        return organization

    @staticmethod
    @transaction.atomic
    def invite_member(organization: Organization, email: str, role: int, invited_by) -> Invitation:
        """Invite a new member to an organization."""
        from datetime import timedelta

        if Membership.objects.filter(
            user__email=email, organization=organization, status=MembershipStatus.ACTIVE
        ).exists():
            raise ValidationError(_("Usuário já é membro desta organização."))

        invitation = Invitation.objects.create(
            email=email,
            organization=organization,
            role=role,
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=7),
            status=InvitationStatus.PENDING,
        )

        logger.info(f"Invitation sent to {email} for organization {organization.id}")
        return invitation

    @staticmethod
    @transaction.atomic
    def accept_invitation(invitation: Invitation, user) -> Membership:
        """Accept an invitation and create membership."""
        if invitation.is_expired:
            invitation.status = InvitationStatus.EXPIRED
            invitation.save()
            raise ValidationError(_("Convite expirado."))

        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = timezone.now()
        invitation.save()

        membership, created = Membership.objects.get_or_create(
            user=user,
            organization=invitation.organization,
            defaults={
                "role": invitation.role,
                "status": MembershipStatus.ACTIVE,
                "invited_by": invitation.invited_by,
            },
        )

        if not created:
            membership.status = MembershipStatus.ACTIVE
            membership.role = invitation.role
            membership.save()

        logger.info(f"Invitation accepted by user {user.id} for organization {invitation.organization.id}")
        return membership

    @staticmethod
    @transaction.atomic
    def remove_member(organization: Organization, user, removed_by) -> None:
        """Remove a member from an organization."""
        if user == organization.owner:
            raise PermissionDeniedError(_("Não é possível remover o proprietário da organização."))

        membership = Membership.objects.filter(
            user=user, organization=organization, status=MembershipStatus.ACTIVE
        ).first()

        if not membership:
            raise NotFoundException(_("Membro não encontrado."))

        membership.status = MembershipStatus.INACTIVE
        membership.save()

        logger.info(f"User {user.id} removed from organization {organization.id} by {removed_by.id}")

    @staticmethod
    def update_member_role(organization: Organization, user, new_role: int) -> Membership:
        """Update a member's role."""
        if user == organization.owner:
            raise PermissionDeniedError(_("Não é possível alterar o papel do proprietário."))

        membership = Membership.objects.filter(
            user=user, organization=organization, status=MembershipStatus.ACTIVE
        ).first()

        if not membership:
            raise NotFoundException(_("Membro não encontrado."))

        membership.role = new_role
        membership.save()

        return membership
