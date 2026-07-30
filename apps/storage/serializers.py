"""Serializers for storage app."""

from rest_framework import serializers
from apps.storage.models import StorageBackendConfig, StoredObject


class StorageBackendConfigSerializer(serializers.ModelSerializer):
    """Serializer for StorageBackendConfig model."""

    organization_name = serializers.StringRelatedField(
        source="organization", read_only=True
    )
    backend_type_display = serializers.CharField(
        source="get_backend_type_display", read_only=True
    )

    class Meta:
        model = StorageBackendConfig
        fields = (
            "id",
            "name",
            "backend_type",
            "backend_type_display",
            "config_encrypted",
            "is_default",
            "organization",
            "organization_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class StoredObjectSerializer(serializers.ModelSerializer):
    """Serializer for StoredObject model."""

    uploaded_by_email = serializers.StringRelatedField(
        source="uploaded_by", read_only=True, default=None
    )

    class Meta:
        model = StoredObject
        fields = (
            "id",
            "key",
            "bucket",
            "size",
            "content_type",
            "checksum",
            "uploaded_by",
            "uploaded_by_email",
            "organization",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
