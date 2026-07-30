from rest_framework import serializers
from apps.quotas.models import QuotaDefinition, QuotaAllocation


class QuotaDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for QuotaDefinition model."""

    class Meta:
        model = QuotaDefinition
        fields = (
            "id", "code", "name", "unit", "description",
            "default_limit", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class QuotaAllocationSerializer(serializers.ModelSerializer):
    """Serializer for QuotaAllocation model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    definition_code = serializers.CharField(
        source="definition.code", read_only=True
    )
    definition_name = serializers.CharField(
        source="definition.name", read_only=True
    )
    definition_unit = serializers.CharField(
        source="definition.unit", read_only=True
    )
    remaining = serializers.IntegerField(read_only=True)
    is_exceeded = serializers.BooleanField(read_only=True)

    class Meta:
        model = QuotaAllocation
        fields = (
            "id", "organization", "organization_name",
            "definition", "definition_code", "definition_name", "definition_unit",
            "limit", "used", "remaining", "is_exceeded",
            "period_start", "period_end",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class QuotaUsageUpdateSerializer(serializers.Serializer):
    """Serializer for updating quota usage."""

    amount = serializers.IntegerField(
        min_value=1,
        help_text="Amount to increment usage by",
    )
