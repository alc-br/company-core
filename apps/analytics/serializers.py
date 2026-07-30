"""Serializers for analytics app."""

from rest_framework import serializers
from apps.analytics.models import AnalyticsEvent, AnalyticsAggregation


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsEvent model (read-only)."""

    user_email = serializers.StringRelatedField(
        source="user", read_only=True, default=None
    )

    class Meta:
        model = AnalyticsEvent
        fields = (
            "id",
            "organization",
            "user",
            "user_email",
            "event_type",
            "module",
            "metadata",
            "timestamp",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AnalyticsAggregationSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsAggregation model."""

    class Meta:
        model = AnalyticsAggregation
        fields = (
            "id",
            "organization",
            "period",
            "module",
            "metric",
            "value",
        )
        read_only_fields = ("id",)
