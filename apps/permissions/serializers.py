from rest_framework import serializers
from apps.permissions.models import Permission, Role, RolePermission


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model."""

    class Meta:
        model = Permission
        fields = ("id", "code", "name", "description", "module")
        read_only_fields = ("id",)


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    permission_codes = serializers.PrimaryKeyRelatedField(
        source="permissions",
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        required=False,
    )
    permissions_detail = PermissionSerializer(
        source="permissions",
        many=True,
        read_only=True,
    )
    permissions_count = serializers.IntegerField(
        source="permissions.count",
        read_only=True,
    )

    class Meta:
        model = Role
        fields = (
            "id", "name", "organization", "organization_name",
            "is_default",
            "permission_codes", "permissions_detail", "permissions_count",
        )
        read_only_fields = ("id", "organization", "organization_name", "permissions_detail", "permissions_count")


class RoleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for role list views."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    permissions_count = serializers.IntegerField(
        source="permissions.count",
        read_only=True,
    )

    class Meta:
        model = Role
        fields = (
            "id", "name", "organization_name", "is_default", "permissions_count",
        )
        read_only_fields = fields


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission through model."""

    role_name = serializers.CharField(
        source="role.name", read_only=True
    )
    permission_code = serializers.CharField(
        source="permission.code", read_only=True
    )
    permission_name = serializers.CharField(
        source="permission.name", read_only=True
    )

    class Meta:
        model = RolePermission
        fields = (
            "id", "role", "role_name", "permission", "permission_code",
            "permission_name",
        )
        read_only_fields = ("id", "role_name", "permission_code", "permission_name")
