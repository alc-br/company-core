def get_user_permissions(user_id, organization_id):
    from apps.permissions.models import Role, RolePermission, Permission
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
