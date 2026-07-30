from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model (read-only)."""

    actor_email = serializers.CharField(
        source="actor.email", read_only=True, default=None
    )
    actor_display_name = serializers.CharField(
        source="actor.get_display_name", read_only=True, default=None
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )

    class Meta:
        model = AuditLog
        fields = (
            "id", "actor", "actor_email", "actor_display_name",
            "actor_type", "action", "target_type", "target_id",
            "ip_address", "user_agent", "metadata",
            "organization", "organization_name",
            "created_at", "updated_at",
        )
        read_only_fields = fields
