"""DRF API ViewSets for storage app."""

import logging
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.storage.models import StorageBackendConfig, StoredObject
from apps.storage.serializers import (
    StorageBackendConfigSerializer,
    StoredObjectSerializer,
)
from apps.storage.selectors import (
    get_storage_backend_queryset,
    get_stored_object_queryset,
)

logger = logging.getLogger(__name__)


class StorageBackendConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for StorageBackendConfig model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "backend_type", "is_default", "created_at"]

    def get_serializer_class(self):
        return StorageBackendConfigSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_storage_backend_queryset(
            organization_id=org_id,
            backend_type=self.request.query_params.get("backend_type", type=int),
            is_default=self.request.query_params.get("is_default", type=str),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def set_default(self, request, pk=None):
        """Set this backend as the default for the organization."""
        backend = self.get_object()
        org_id = backend.organization_id
        if org_id:
            StorageBackendConfig.objects.filter(
                organization_id=org_id
            ).update(is_default=False)
            backend.is_default = True
            backend.save(update_fields=["is_default"])
        serializer = self.get_serializer(backend)
        return Response(serializer.data)


class StoredObjectViewSet(viewsets.ModelViewSet):
    """ViewSet for StoredObject model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["key", "content_type"]
    ordering_fields = ["-created_at", "key", "size", "content_type"]

    def get_serializer_class(self):
        return StoredObjectSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_stored_object_queryset(
            organization_id=org_id,
            bucket=self.request.query_params.get("bucket"),
            content_type=self.request.query_params.get("content_type"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get storage statistics for the organization."""
        org_id = getattr(request, "tenant", None)
        qs = self.get_queryset()
        from django.db.models import Sum, Count
        stats = qs.aggregate(
            total_objects=Count("id"),
            total_size=Sum("size"),
            total_buckets=Count("bucket", distinct=True),
        )
        return Response({"stats": stats})
