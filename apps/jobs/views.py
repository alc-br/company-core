"""DRF API ViewSets for jobs app."""

import logging
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer
from apps.jobs.selectors import get_job_queryset

logger = logging.getLogger(__name__)


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for Job model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "task_path"]
    ordering_fields = ["priority", "-created_at", "status", "name"]

    def get_serializer_class(self):
        return JobSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_job_queryset(
            organization_id=org_id,
            status=self.request.query_params.get("status", type=int),
            priority=self.request.query_params.get("priority", type=int),
            task_path=self.request.query_params.get("task_path"),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def retry(self, request, pk=None):
        """Retry a failed job."""
        job = self.get_object()
        job.status = 0
        job.retries = 0
        job.last_error = ""
        job.started_at = None
        job.completed_at = None
        job.save()
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel a pending or running job."""
        job = self.get_object()
        from apps.common.constants import JobStatus
        job.status = JobStatus.CANCELLED
        job.save()
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get job statistics."""
        qs = self.get_queryset()
        from django.db.models import Count
        stats = qs.values("status").annotate(count=Count("id"))
        return Response({"stats": list(stats)})
