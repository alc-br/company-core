import logging
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.quotas.models import QuotaDefinition, QuotaAllocation
from apps.quotas.serializers import (
    QuotaDefinitionSerializer,
    QuotaAllocationSerializer,
    QuotaUsageUpdateSerializer,
)
from apps.quotas.services import QuotaService
from apps.quotas.selectors import (
    get_quota_definition_queryset,
    get_quota_allocation_queryset,
)

logger = logging.getLogger(__name__)

app_name = "quotas"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_quotas(request):
    quotas = get_all_quotas(request.tenant.id) if request.tenant else []
    return render(request, "quotas/list.html", {"quotas": quotas})


def get_all_quotas(org_id):
    from apps.quotas.models import QuotaAllocation
    return QuotaAllocation.objects.filter(organization_id=org_id).select_related("definition")


# ─── QuotaDefinition CRUD Template Views (Admin Only) ──────────────


class QuotaDefinitionForm(forms.ModelForm):
    class Meta:
        model = QuotaDefinition
        fields = ['code', 'name', 'unit', 'description', 'default_limit']


@login_required
def create_quota(request):
    if request.method == 'POST':
        form = QuotaDefinitionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Definição de quota criada com sucesso!")
            return redirect('quotas:list')
    else:
        form = QuotaDefinitionForm()
    return render(request, 'quotas/quota_form.html', {'form': form})


@login_required
def edit_quota(request, pk):
    quota = get_object_or_404(QuotaDefinition, pk=pk)
    if request.method == 'POST':
        form = QuotaDefinitionForm(request.POST, instance=quota)
        if form.is_valid():
            form.save()
            messages.success(request, "Definição de quota atualizada com sucesso!")
            return redirect('quotas:list')
    else:
        form = QuotaDefinitionForm(instance=quota)
    return render(request, 'quotas/quota_form.html', {'form': form, 'object': quota})


@login_required
def delete_quota(request, pk):
    quota = get_object_or_404(QuotaDefinition, pk=pk)
    if request.method == 'POST':
        quota.delete()
        messages.success(request, "Definição de quota excluída com sucesso!")
        return redirect('quotas:list')
    return render(request, 'quotas/quota_confirm_delete.html', {
        'object': quota,
        'cancel_url': reverse('quotas:list'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class QuotaDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for QuotaDefinition model. Admin-only."""

    queryset = QuotaDefinition.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["code", "name", "default_limit"]

    def get_serializer_class(self):
        return QuotaDefinitionSerializer

    def get_queryset(self):
        return get_quota_definition_queryset(
            code=self.request.query_params.get("code"),
        )

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticated()]


class QuotaAllocationViewSet(viewsets.ModelViewSet):
    """ViewSet for QuotaAllocation model."""

    queryset = QuotaAllocation.objects.select_related("definition", "organization")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["used", "limit", "period_start"]

    def get_serializer_class(self):
        return QuotaAllocationSerializer

    def get_queryset(self):
        return get_quota_allocation_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            definition_id=self.request.query_params.get("definition_id"),
            code=self.request.query_params.get("code"),
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def increment(self, request, pk=None):
        """Increment usage for a quota allocation."""
        allocation = self.get_object()
        serializer = QuotaUsageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        try:
            QuotaService.check_quota(
                organization_id=allocation.organization_id,
                quota_code=allocation.definition.code,
                increment=amount,
            )
            QuotaService.increment_usage(
                organization_id=allocation.organization_id,
                quota_code=allocation.definition.code,
                amount=amount,
            )
            # Refresh the object to get updated values
            allocation.refresh_from_db()
            return Response(self.get_serializer(allocation).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def status(self, request):
        """Get quota status for an organization (optionally filtered by code)."""
        organization_id = request.query_params.get("organization_id")
        code = request.query_params.get("code")

        if not organization_id:
            return Response(
                {"error": "organization_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if code:
            result = QuotaService.get_quota_status(organization_id, code)
            if not result:
                return Response(
                    {"error": f"No allocation found for quota '{code}'."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(result)
        else:
            # Return all quota statuses for the organization
            allocations = get_quota_allocation_queryset(organization_id=organization_id)
            statuses = []
            for alloc in allocations:
                statuses.append({
                    "code": alloc.definition.code,
                    "name": alloc.definition.name,
                    "unit": alloc.definition.unit,
                    "limit": alloc.limit,
                    "used": alloc.used,
                    "remaining": alloc.remaining,
                    "is_exceeded": alloc.is_exceeded,
                })
            return Response(statuses)
