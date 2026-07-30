import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.audit.selectors import get_audit_log_queryset

logger = logging.getLogger(__name__)

app_name = "audit"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_logs(request):
    qs = AuditLog.objects.filter(organization=request.tenant) if request.tenant else AuditLog.objects.none()
    logs = qs.order_by("-created_at")[:100]
    return render(request, "audit/logs.html", {"logs": logs})


# ─── DRF API ViewSets ───────────────────────────────────────────────


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AuditLog model (read-only)."""

    queryset = AuditLog.objects.select_related("actor", "organization")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["action", "target_type"]
    ordering_fields = ["created_at", "action", "target_type"]

    def get_serializer_class(self):
        return AuditLogSerializer

    def get_queryset(self):
        return get_audit_log_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            actor_id=self.request.query_params.get("actor_id"),
            action=self.request.query_params.get("action"),
            target_type=self.request.query_params.get("target_type"),
            target_id=self.request.query_params.get("target_id"),
        )
