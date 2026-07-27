import logging
from django.db import transaction
from apps.permissions.models import Role, Permission, RolePermission
from apps.common.exceptions import NotFoundException, PermissionDeniedError

logger = logging.getLogger(__name__)


class PermissionService:
    @staticmethod
    def check_permission(user_id, organization_id, permission_code):
        """Check if user has a specific permission in organization."""
        from apps.organizations.models import Membership
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
        permission_codes = permission_codes or []
        role = Role.objects.create(organization=organization, name=name, is_default=is_default)
        if permission_codes:
            permissions = Permission.objects.filter(code__in=permission_codes)
            RolePermission.objects.bulk_create([
                RolePermission(role=role, permission=p) for p in permissions
            ])
        return role
