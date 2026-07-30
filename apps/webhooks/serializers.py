"""Serializers for webhooks app."""

from rest_framework import serializers
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for WebhookEndpoint model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True
    )

    class Meta:
        model = WebhookEndpoint
        fields = (
            "id",
            "url",
            "secret_encrypted",
            "events",
            "organization",
            "organization_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for WebhookDelivery model (read-only)."""

    endpoint_url = serializers.StringRelatedField(
        source="endpoint", read_only=True
    )

    class Meta:
        model = WebhookDelivery
        fields = (
            "id",
            "endpoint",
            "endpoint_url",
            "event_type",
            "payload",
            "status",
            "attempts",
            "response_code",
            "last_attempt_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
