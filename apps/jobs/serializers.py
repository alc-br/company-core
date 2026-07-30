"""Serializers for jobs app."""

from rest_framework import serializers
from apps.jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True, default=None
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Job
        fields = (
            "id",
            "name",
            "task_path",
            "status",
            "status_display",
            "priority",
            "retries",
            "max_retries",
            "last_error",
            "scheduled_at",
            "started_at",
            "completed_at",
            "organization",
            "organization_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "retries", "last_error", "started_at", "completed_at")
