from rest_framework import serializers
from apps.organizations.models import Organization, Membership, Invitation
from apps.common.constants import MembershipRole, MembershipStatus, InvitationStatus


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Organization
        fields = (
            "id", "name", "slug", "owner", "status", "status_display",
            "metadata", "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def validate_status(self, value):
        """Validate status is a valid MembershipStatus choice."""
        valid_choices = [choice.value for choice in MembershipStatus]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {valid_choices}"
            )
        return value


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for organization list views."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "status", "status_display", "created_at")
        read_only_fields = fields


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_display_name = serializers.CharField(
        source="user.get_display_name", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    role_display = serializers.CharField(
        source="get_role_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Membership
        fields = (
            "id", "user", "user_email", "user_display_name",
            "organization", "organization_name",
            "role", "role_display", "status", "status_display",
            "invited_by", "joined_at", "created_at", "updated_at",
        )
        read_only_fields = ("id", "joined_at", "created_at", "updated_at")


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for Invitation model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    role_display = serializers.CharField(
        source="get_role_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id", "email", "organization", "organization_name",
            "role", "role_display", "token", "status", "status_display",
            "accepted_at", "expires_at", "is_expired",
            "invited_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "token", "accepted_at", "created_at", "updated_at")

    def validate_role(self, value):
        """Validate role is a valid MembershipRole choice."""
        valid_choices = [choice.value for choice in MembershipRole]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {valid_choices}"
            )
        return value

    def validate_status(self, value):
        """Validate status is a valid InvitationStatus choice."""
        valid_choices = [choice.value for choice in InvitationStatus]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {valid_choices}"
            )
        return value


class InvitationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invitations (token auto-generated)."""

    class Meta:
        model = Invitation
        fields = ("email", "organization", "role", "expires_at", "invited_by")
        read_only_fields = ("token",)
