from rest_framework import serializers
from apps.settings.models import TenantSetting, GlobalSetting


class TenantSettingSerializer(serializers.ModelSerializer):
    """Serializer for TenantSetting model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = TenantSetting
        fields = (
            "id", "organization", "organization_name",
            "key", "value", "environment",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TenantSettingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tenant settings (key+environment identify the record)."""

    class Meta:
        model = TenantSetting
        fields = ("key", "value", "environment")


class GlobalSettingSerializer(serializers.ModelSerializer):
    """Serializer for GlobalSetting model."""

    class Meta:
        model = GlobalSetting
        fields = ("id", "key", "value", "description")
        read_only_fields = ("id",)
