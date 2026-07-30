"""DRF API ViewSets for analytics app."""

import logging
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.models import AnalyticsEvent, AnalyticsAggregation
from apps.analytics.serializers import (
    AnalyticsEventSerializer,
    AnalyticsAggregationSerializer,
)
from apps.analytics.selectors import (
    get_analytics_event_queryset,
    get_analytics_aggregation_queryset,
)

logger = logging.getLogger(__name__)


class AnalyticsEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AnalyticsEvent model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-timestamp", "event_type", "module"]

    def get_serializer_class(self):
        return AnalyticsEventSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_analytics_event_queryset(
            organization_id=org_id,
            user_id=self.request.query_params.get("user_id", type=int),
            event_type=self.request.query_params.get("event_type"),
            module=self.request.query_params.get("module"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get event statistics."""
        qs = self.get_queryset()
        from django.db.models import Count
        stats = qs.values("event_type").annotate(count=Count("id"))
        return Response({"stats": list(stats)})


class AnalyticsAggregationViewSet(viewsets.ModelViewSet):
    """ViewSet for AnalyticsAggregation model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-period", "module", "metric"]

    def get_serializer_class(self):
        return AnalyticsAggregationSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_analytics_aggregation_queryset(
            organization_id=org_id,
            module=self.request.query_params.get("module"),
            period_from=self.request.query_params.get("period_from"),
            period_to=self.request.query_params.get("period_to"),
        )
