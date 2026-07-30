"""Serializers for notifications app."""

from rest_framework import serializers
from apps.notifications.models import (
    NotificationChannel,
    NotificationTemplate,
    NotificationLog,
)


class NotificationChannelSerializer(serializers.ModelSerializer):
    """Serializer for NotificationChannel model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True
    )
    type_display = serializers.CharField(
        source="get_type_display", read_only=True
    )

    class Meta:
        model = NotificationChannel
        fields = (
            "id",
            "type",
            "type_display",
            "name",
            "organization",
            "organization_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class NotificationChannelListSerializer(NotificationChannelSerializer):
    """Lightweight list serializer for NotificationChannel."""

    class Meta(NotificationChannelSerializer.Meta):
        fields = ("id", "type", "type_display", "name", "is_active", "created_at")


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model."""

    class Meta:
        model = NotificationTemplate
        fields = (
            "id",
            "code",
            "subject",
            "body_html",
            "body_text",
            "channel",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for NotificationLog model (read-only)."""

    channel_name = serializers.StringRelatedField(
        source="channel", read_only=True, default=None
    )
    template_code = serializers.StringRelatedField(
        source="template", read_only=True, default=None
    )

    class Meta:
        model = NotificationLog
        fields = (
            "id",
            "channel",
            "channel_name",
            "recipient",
            "template",
            "template_code",
            "status",
            "sent_at",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
