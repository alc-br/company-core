import logging
from django.db import transaction
from apps.permissions.models import Role, Permission, RolePermission
from apps.common.exceptions import NotFoundException, PermissionDeniedError

logger = logging.getLogger(__name__)


class PermissionService:
    """Service layer for permission operations."""

    @staticmethod
    def check_permission(user_id, organization_id, permission_code):
        """Check if user has a specific permission in organization."""
        from apps.organizations.selectors import get_user_role
        from apps.common.constants import MembershipRole

        role = get_user_role(user_id, organization_id)
        if role == MembershipRole.OWNER:
            return True

        if role is None:
            return False

        role_obj = Role.objects.filter(
            organization_id=organization_id,
            memberships__user_id=user_id,
        ).first()

        if not role_obj:
            return True  # Fall back to membership-based permission

        return RolePermission.objects.filter(
            role=role_obj, permission__code=permission_code
        ).exists()

    @staticmethod
    @transaction.atomic
    def create_role(organization, name, permission_codes=None, is_default=False):
        """Create a new role with optional permissions."""
        permission_codes = permission_codes or []

        if Role.objects.filter(organization=organization, name=name).exists():
            from apps.common.exceptions import ValidationError
            raise ValidationError(
                message=f"Role '{name}' already exists in this organization."
            )

        role = Role.objects.create(
            organization=organization, name=name, is_default=is_default,
        )

        if permission_codes:
            permissions = Permission.objects.filter(code__in=permission_codes)
            RolePermission.objects.bulk_create([
                RolePermission(role=role, permission=p) for p in permissions
            ])

        logger.info(f"Role '{name}' created in organization {organization.id}")
        return role

    @staticmethod
    @transaction.atomic
    def update_role(role, name=None, is_default=None, permission_codes=None):
        """Update a role's properties and permissions."""
        if name is not None:
            role.name = name
        if is_default is not None:
            role.is_default = is_default
        role.save()

        if permission_codes is not None:
            # Replace all permissions
            RolePermission.objects.filter(role=role).delete()
            permissions = Permission.objects.filter(code__in=permission_codes)
            RolePermission.objects.bulk_create([
                RolePermission(role=role, permission=p) for p in permissions
            ])

        logger.info(f"Role {role.id} updated")
        return role

    @staticmethod
    @transaction.atomic
    def delete_role(role):
        """Delete a role."""
        role_id = role.id
        role_name = role.name
        role.delete()
        logger.info(f"Role '{role_name}' (id={role_id}) deleted")

    @staticmethod
    @transaction.atomic
    def add_permission_to_role(role, permission_code):
        """Add a permission to a role."""
        permission = Permission.objects.filter(code=permission_code).first()
        if not permission:
            raise NotFoundException(
                message=f"Permission '{permission_code}' not found.",
                resource_type="permission",
            )

        role_permission, created = RolePermission.objects.get_or_create(
            role=role, permission=permission,
        )
        if created:
            logger.info(f"Permission '{permission_code}' added to role '{role.name}'")
        return role_permission

    @staticmethod
    @transaction.atomic
    def remove_permission_from_role(role, permission_code):
        """Remove a permission from a role."""
        deleted = RolePermission.objects.filter(
            role=role, permission__code=permission_code,
        ).delete()
        if deleted[0] > 0:
            logger.info(f"Permission '{permission_code}' removed from role '{role.name}'")
        return deleted
