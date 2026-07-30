"""DRF API ViewSets for webhooks app."""

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

from apps.webhooks.models import WebhookEndpoint, WebhookDelivery
from apps.webhooks.serializers import (
    WebhookEndpointSerializer,
    WebhookDeliverySerializer,
)
from apps.webhooks.selectors import (
    get_webhook_endpoint_queryset,
    get_webhook_delivery_queryset,
)

logger = logging.getLogger(__name__)

app_name = "webhooks"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_endpoints(request):
    endpoints = WebhookEndpoint.objects.filter(organization=request.tenant).order_by('-created_at') if request.tenant else []
    return render(request, 'webhooks/endpoints.html', {'endpoints': endpoints})


# ─── Endpoint CRUD ─────────────────────────────────────────────────


class WebhookEndpointForm(forms.ModelForm):
    events = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '["event1", "event2"]}'}),
        required=False,
        help_text="JSON array com nomes dos eventos"
    )

    class Meta:
        model = WebhookEndpoint
        fields = ['url', 'events', 'is_active']

    def clean_events(self):
        import json
        val = self.cleaned_data.get('events', '')
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError("JSON inválido para eventos.")
        return []


@login_required
def create_endpoint(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('webhooks:list')
    if request.method == 'POST':
        form = WebhookEndpointForm(request.POST)
        if form.is_valid():
            endpoint = form.save(commit=False)
            endpoint.organization = request.tenant
            endpoint.save()
            messages.success(request, "Endpoint criado com sucesso!")
            return redirect('webhooks:list')
    else:
        form = WebhookEndpointForm()
    return render(request, 'webhooks/endpoint_form.html', {'form': form})


@login_required
def edit_endpoint(request, pk):
    endpoint = get_object_or_404(WebhookEndpoint, pk=pk)
    if request.method == 'POST':
        form = WebhookEndpointForm(request.POST, instance=endpoint)
        if form.is_valid():
            form.save()
            messages.success(request, "Endpoint atualizado com sucesso!")
            return redirect('webhooks:list')
    else:
        form = WebhookEndpointForm(instance=endpoint)
    return render(request, 'webhooks/endpoint_form.html', {'form': form, 'object': endpoint})


@login_required
def delete_endpoint(request, pk):
    endpoint = get_object_or_404(WebhookEndpoint, pk=pk)
    if request.method == 'POST':
        endpoint.delete()
        messages.success(request, "Endpoint excluído com sucesso!")
        return redirect('webhooks:list')
    return render(request, 'webhooks/endpoint_confirm_delete.html', {
        'object': endpoint,
        'cancel_url': reverse('webhooks:list'),
    })


@login_required
def test_endpoint(request, pk):
    endpoint = get_object_or_404(WebhookEndpoint, pk=pk)
    try:
        from apps.webhooks.services import WebhookService
        WebhookService.deliver(endpoint, "test.event", {"test": True, "message": "Teste de webhook"})
        messages.success(request, "Teste enviado com sucesso! Verifique as entregas.")
    except Exception as e:
        messages.error(request, f"Erro ao enviar teste: {str(e)}")
    return redirect('webhooks:list')


# ─── DRF API ViewSets ───────────────────────────────────────────────


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """ViewSet for WebhookEndpoint model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["url", "is_active", "created_at"]

    def get_serializer_class(self):
        return WebhookEndpointSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_webhook_endpoint_queryset(
            organization_id=org_id,
            is_active=self.request.query_params.get("is_active", type=str),
            event_type=self.request.query_params.get("event_type"),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a webhook endpoint."""
        endpoint = self.get_object()
        endpoint.is_active = not endpoint.is_active
        endpoint.save(update_fields=["is_active"])
        serializer = self.get_serializer(endpoint)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def test_delivery(self, request, pk=None):
        """Send a test payload to this webhook endpoint."""
        endpoint = self.get_object()
        try:
            from apps.webhooks.services import WebhookService
            WebhookService.deliver(endpoint, "test.event", {"test": True})
            return Response({"status": "queued"})
        except Exception as e:
            logger.exception("Test delivery failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for WebhookDelivery model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-created_at", "event_type", "status"]

    def get_serializer_class(self):
        return WebhookDeliverySerializer

    def get_queryset(self):
        return get_webhook_delivery_queryset(
            endpoint_id=self.request.query_params.get("endpoint_id", type=int),
            event_type=self.request.query_params.get("event_type"),
            status=self.request.query_params.get("status"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get webhook delivery statistics."""
        qs = self.get_queryset()
        from django.db.models import Count
        stats = qs.values("status").annotate(count=Count("id"))
        return Response({"stats": list(stats)})
