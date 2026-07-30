from typing import Optional
from django.db.models import QuerySet
from apps.permissions.models import Permission, Role, RolePermission


def get_user_permissions(user_id, organization_id):
    """Get all permissions for a user within an organization."""
    from apps.common.constants import MembershipRole
    from apps.organizations.selectors import get_user_role

    role = get_user_role(user_id, organization_id)
    if role == MembershipRole.OWNER:
        return Permission.objects.all()

    role_obj = Role.objects.filter(
        organization_id=organization_id, memberships__user_id=user_id
    ).first()
    if not role_obj:
        return Permission.objects.none()

    return Permission.objects.filter(roles=role_obj)


def get_permission_queryset(
    *,
    code: Optional[str] = None,
    module: Optional[str] = None,
) -> QuerySet[Permission]:
    """Get permissions queryset for API views."""
    queryset = Permission.objects.all()

    if code is not None:
        queryset = queryset.filter(code=code)

    if module is not None:
        queryset = queryset.filter(module=module)

    return queryset


def get_role_queryset(
    *,
    organization_id: Optional[int] = None,
    is_default: Optional[bool] = None,
) -> QuerySet[Role]:
    """Get roles queryset for API views."""
    queryset = Role.objects.select_related("organization").prefetch_related("permissions")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_default is not None:
        queryset = queryset.filter(is_default=is_default)

    return queryset


def get_role_permission_queryset(
    *,
    role_id: Optional[int] = None,
) -> QuerySet[RolePermission]:
    """Get role permissions queryset for API views."""
    queryset = RolePermission.objects.select_related("role", "permission")

    if role_id is not None:
        queryset = queryset.filter(role_id=role_id)

    return queryset
