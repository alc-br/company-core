"""DRF API ViewSets for search app."""

import logging
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.search.models import SearchIndex
from apps.search.serializers import SearchIndexSerializer
from apps.search.selectors import get_search_index_queryset

logger = logging.getLogger(__name__)


class SearchIndexViewSet(viewsets.ModelViewSet):
    """ViewSet for SearchIndex model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-indexed_at", "content_type"]

    def get_serializer_class(self):
        return SearchIndexSerializer

    def get_queryset(self):
        return get_search_index_queryset(
            content_type=self.request.query_params.get("content_type"),
            search=self.request.query_params.get("search"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def fulltext_search(self, request):
        """Perform a full-text search across all indexed content."""
        query = request.query_params.get("q", "")
        if not query:
            return Response({"error": "q parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = request.query_params.get("content_type")
        results = get_search_index_queryset(
            content_type=content_type,
            search=query,
        )
        serializer = SearchIndexSerializer(results, many=True)
        return Response({"query": query, "results": serializer.data, "count": results.count()})

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def clear_type(self, request):
        """Clear all search indices for a given content type."""
        content_type = request.query_params.get("content_type")
        if not content_type:
            return Response({"error": "content_type parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = SearchIndex.objects.filter(content_type=content_type).delete()
        return Response({"deleted": deleted})
