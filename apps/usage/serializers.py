"""Serializers for usage app."""

from rest_framework import serializers
from apps.usage.models import UsageRecord


class UsageRecordSerializer(serializers.ModelSerializer):
    """Serializer for UsageRecord model."""

    user_email = serializers.StringRelatedField(
        source="user", read_only=True, default=None
    )
    metric_type_display = serializers.CharField(
        source="get_metric_type_display", read_only=True
    )

    class Meta:
        model = UsageRecord
        fields = (
            "id",
            "organization",
            "user",
            "user_email",
            "metric_type",
            "metric_type_display",
            "value",
            "unit",
            "period",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
