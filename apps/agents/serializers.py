"""Serializers for agents app."""

from rest_framework import serializers
from apps.agents.models import Agent, AgentTool, AgentExecution


class AgentToolSerializer(serializers.ModelSerializer):
    """Serializer for AgentTool model."""

    class Meta:
        model = AgentTool
        fields = (
            "id",
            "name",
            "code",
            "description",
            "handler_path",
            "input_schema",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for Agent model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True
    )
    provider_name = serializers.StringRelatedField(
        source="provider", read_only=True, default=None
    )
    tool_ids = serializers.PrimaryKeyRelatedField(
        source="tools",
        queryset=AgentTool.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    tools = AgentToolSerializer(source="tools", many=True, read_only=True)

    class Meta:
        model = Agent
        fields = (
            "id",
            "name",
            "description",
            "system_prompt",
            "provider",
            "provider_name",
            "model_id",
            "temperature",
            "memory_config",
            "organization",
            "organization_name",
            "is_active",
            "tool_ids",
            "tools",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Serializer for AgentExecution model (read-only)."""

    agent_name = serializers.StringRelatedField(
        source="agent", read_only=True
    )

    class Meta:
        model = AgentExecution
        fields = (
            "id",
            "agent",
            "agent_name",
            "status",
            "input_data",
            "output_data",
            "tokens_used",
            "duration_ms",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
