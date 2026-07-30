"""Serializers for search app."""

from rest_framework import serializers
from apps.search.models import SearchIndex


class SearchIndexSerializer(serializers.ModelSerializer):
    """Serializer for SearchIndex model."""

    class Meta:
        model = SearchIndex
        fields = (
            "id",
            "content_type",
            "object_id",
            "content",
            "metadata",
            "indexed_at",
        )
        read_only_fields = ("id", "indexed_at")
