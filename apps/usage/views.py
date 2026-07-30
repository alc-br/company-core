"""DRF API ViewSets for usage app."""

import logging
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usage.models import UsageRecord
from apps.usage.serializers import UsageRecordSerializer
from apps.usage.selectors import get_usage_record_queryset

logger = logging.getLogger(__name__)


class UsageRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for UsageRecord model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-period", "metric_type", "-created_at"]

    def get_serializer_class(self):
        return UsageRecordSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_usage_record_queryset(
            organization_id=org_id,
            user_id=self.request.query_params.get("user_id", type=int),
            metric_type=self.request.query_params.get("metric_type", type=int),
            period_from=self.request.query_params.get("period_from"),
            period_to=self.request.query_params.get("period_to"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get usage statistics."""
        qs = self.get_queryset()
        from django.db.models import Sum, Count
        stats = qs.values("metric_type").annotate(
            total_value=Sum("value"),
            record_count=Count("id"),
        )
        return Response({"stats": list(stats)})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def by_period(self, request):
        """Get usage aggregated by period."""
        qs = self.get_queryset()
        from django.db.models import Sum
        data = qs.values("period", "metric_type", "unit").annotate(
            total_value=Sum("value")
        ).order_by("period")
        return Response({"data": list(data)})
