import logging
from django.db import transaction
from django.utils import timezone
from apps.users.models import CustomUser
from apps.common.exceptions import NotFoundException, ValidationError


logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user operations."""

    @staticmethod
    @transaction.atomic
    def update_profile(user, **kwargs):
        """Update user profile fields."""
        allowed_fields = {"first_name", "last_name", "avatar", "bio", "timezone", "language"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
        user.save()
        logger.info(f"User {user.id} profile updated")
        return user

    @staticmethod
    @transaction.atomic
    def deactivate_user(user):
        """Deactivate a user account."""
        user.is_active = False
        user.save()
        logger.info(f"User {user.id} deactivated")
        return user

    @staticmethod
    @transaction.atomic
    def activate_user(user):
        """Activate a user account."""
        user.is_active = True
        user.save()
        logger.info(f"User {user.id} activated")
        return user

    @staticmethod
    @transaction.atomic
    def toggle_staff_status(user):
        """Toggle user's staff status."""
        user.is_staff = not user.is_staff
        user.save()
        logger.info(f"User {user.id} staff status set to {user.is_staff}")
        return user

    @staticmethod
    def get_user_with_memberships(user_id):
        """Get a user with their organization memberships prefetched."""
        try:
            return CustomUser.objects.prefetch_related("memberships__organization").get(id=user_id)
        except CustomUser.DoesNotExist:
            raise NotFoundException(
                message=f"User with id {user_id} not found.",
                resource_type="user",
                resource_id=user_id,
            )

    @staticmethod
    def get_users_for_organization(organization_id, *, is_active=True):
        """Get all users who are members of an organization."""
        from apps.organizations.models import Membership
        from apps.common.constants import MembershipStatus

        queryset = CustomUser.objects.filter(
            memberships__organization_id=organization_id,
            memberships__status=MembershipStatus.ACTIVE,
        ).distinct()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset
