"""Serializers for integrations app."""

from rest_framework import serializers
from apps.integrations.models import Integration, IntegrationLog


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Integration model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True
    )

    class Meta:
        model = Integration
        fields = (
            "id",
            "name",
            "integration_type",
            "credentials_encrypted",
            "status",
            "organization",
            "organization_name",
            "last_health_check",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "last_health_check")


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationLog model (read-only)."""

    integration_name = serializers.StringRelatedField(
        source="integration", read_only=True
    )

    class Meta:
        model = IntegrationLog
        fields = (
            "id",
            "integration",
            "integration_name",
            "action",
            "request_data",
            "response_data",
            "status",
            "duration_ms",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
