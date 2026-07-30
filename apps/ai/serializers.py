"""Serializers for AI app."""

from rest_framework import serializers
from apps.ai.models import AIProviderConfig, AIModelConfig, AICallLog


class AIProviderConfigSerializer(serializers.ModelSerializer):
    """Serializer for AIProviderConfig model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True, default=None
    )
    provider_name_display = serializers.CharField(
        source="get_provider_name_display", read_only=True
    )

    class Meta:
        model = AIProviderConfig
        fields = (
            "id",
            "provider_name",
            "provider_name_display",
            "display_name",
            "api_key_encrypted",
            "models_list",
            "is_default",
            "organization",
            "organization_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AIModelConfigSerializer(serializers.ModelSerializer):
    """Serializer for AIModelConfig model."""

    provider_name = serializers.StringRelatedField(
        source="provider", read_only=True
    )

    class Meta:
        model = AIModelConfig
        fields = (
            "id",
            "model_id",
            "display_name",
            "provider",
            "provider_name",
            "max_tokens",
            "cost_per_1k_input",
            "cost_per_1k_output",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AICallLogSerializer(serializers.ModelSerializer):
    """Serializer for AICallLog model (read-only)."""

    user_email = serializers.StringRelatedField(
        source="user", read_only=True, default=None
    )

    class Meta:
        model = AICallLog
        fields = (
            "id",
            "organization",
            "user",
            "user_email",
            "provider_name",
            "model",
            "tokens_input",
            "tokens_output",
            "cost",
            "latency_ms",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
