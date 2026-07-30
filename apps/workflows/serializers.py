"""Serializers for workflows app."""

from rest_framework import serializers
from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStepLog


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for Workflow model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True
    )

    class Meta:
        model = Workflow
        fields = (
            "id",
            "name",
            "description",
            "steps_config",
            "organization",
            "organization_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowExecution model."""

    workflow_name = serializers.StringRelatedField(
        source="workflow", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = WorkflowExecution
        fields = (
            "id",
            "workflow",
            "workflow_name",
            "status",
            "status_display",
            "current_step",
            "input_data",
            "output_data",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WorkflowStepLogSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowStepLog model (read-only)."""

    class Meta:
        model = WorkflowStepLog
        fields = (
            "id",
            "execution",
            "step_name",
            "status",
            "input_data",
            "output_data",
            "error_message",
            "duration_ms",
            "created_at",
        )
        read_only_fields = fields
