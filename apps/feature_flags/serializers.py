from rest_framework import serializers
from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment


class FeatureFlagSerializer(serializers.ModelSerializer):
    """Serializer for FeatureFlag model."""

    created_by_email = serializers.CharField(
        source="created_by.email", read_only=True, default=None
    )

    class Meta:
        model = FeatureFlag
        fields = (
            "id", "code", "name", "description", "is_active",
            "created_by", "created_by_email",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class FeatureFlagListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for feature flag list views."""

    class Meta:
        model = FeatureFlag
        fields = ("id", "code", "name", "is_active", "created_at")
        read_only_fields = fields


class FeatureFlagAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for FeatureFlagAssignment model."""

    flag_code = serializers.CharField(
        source="flag.code", read_only=True
    )
    flag_name = serializers.CharField(
        source="flag.name", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )
    user_email = serializers.CharField(
        source="user.email", read_only=True, default=None
    )

    class Meta:
        model = FeatureFlagAssignment
        fields = (
            "id", "flag", "flag_code", "flag_name",
            "organization", "organization_name",
            "user", "user_email",
            "environment", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "flag_code", "flag_name", "organization_name", "user_email", "created_at", "updated_at")
