"""DRF API ViewSets for integrations app."""

import logging
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.integrations.models import Integration, IntegrationLog
from apps.integrations.serializers import (
    IntegrationSerializer,
    IntegrationLogSerializer,
)
from apps.integrations.selectors import (
    get_integration_queryset,
    get_integration_log_queryset,
)

logger = logging.getLogger(__name__)

app_name = "integrations"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_integrations(request):
    integrations = Integration.objects.filter(organization=request.tenant).order_by('name') if request.tenant else []
    return render(request, 'integrations/list.html', {'integrations': integrations})


# ─── Integration CRUD ─────────────────────────────────────────────


class IntegrationForm(forms.ModelForm):
    class Meta:
        model = Integration
        fields = ['name', 'integration_type', 'status', 'metadata']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metadata'].required = False


@login_required
def create_integration(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('integrations:list')
    if request.method == 'POST':
        form = IntegrationForm(request.POST)
        if form.is_valid():
            integration = form.save(commit=False)
            integration.organization = request.tenant
            integration.save()
            messages.success(request, "Integração criada com sucesso!")
            return redirect('integrations:list')
    else:
        form = IntegrationForm()
    return render(request, 'integrations/integration_form.html', {'form': form})


@login_required
def edit_integration(request, pk):
    integration = get_object_or_404(Integration, pk=pk)
    if request.method == 'POST':
        form = IntegrationForm(request.POST, instance=integration)
        if form.is_valid():
            form.save()
            messages.success(request, "Integração atualizada com sucesso!")
            return redirect('integrations:list')
    else:
        form = IntegrationForm(instance=integration)
    return render(request, 'integrations/integration_form.html', {'form': form, 'object': integration})


@login_required
def delete_integration(request, pk):
    integration = get_object_or_404(Integration, pk=pk)
    if request.method == 'POST':
        integration.delete()
        messages.success(request, "Integração excluída com sucesso!")
        return redirect('integrations:list')
    return render(request, 'integrations/integration_confirm_delete.html', {
        'object': integration,
        'cancel_url': reverse('integrations:list'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class IntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Integration model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "integration_type"]
    ordering_fields = ["name", "integration_type", "status", "created_at"]

    def get_serializer_class(self):
        return IntegrationSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_integration_queryset(
            organization_id=org_id,
            integration_type=self.request.query_params.get("integration_type"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def health_check(self, request, pk=None):
        """Trigger a health check for this integration."""
        integration = self.get_object()
        try:
            from apps.integrations.services import IntegrationService
            result = IntegrationService.health_check(integration)
            serializer = self.get_serializer(integration)
            return Response({"status": "ok", "integration": serializer.data})
        except Exception as e:
            logger.exception("Health check failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def logs(self, request, pk=None):
        """Get logs for this integration."""
        integration = self.get_object()
        logs = get_integration_log_queryset(integration_id=integration.id)
        serializer = IntegrationLogSerializer(logs, many=True)
        return Response(serializer.data)


class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for IntegrationLog model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-created_at", "action", "status"]

    def get_serializer_class(self):
        return IntegrationLogSerializer

    def get_queryset(self):
        return get_integration_log_queryset(
            integration_id=self.request.query_params.get("integration_id", type=int),
            action=self.request.query_params.get("action"),
            status=self.request.query_params.get("status"),
        )
