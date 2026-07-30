"""DRF API ViewSets for AI app."""

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

from apps.ai.models import AIProviderConfig, AIModelConfig, AICallLog
from apps.ai.serializers import (
    AIProviderConfigSerializer,
    AIModelConfigSerializer,
    AICallLogSerializer,
)
from apps.ai.selectors import (
    get_ai_provider_queryset,
    get_ai_model_config_queryset,
    get_ai_call_log_queryset,
)

logger = logging.getLogger(__name__)

app_name = "ai"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_providers(request):
    providers = AIProviderConfig.objects.filter(organization=request.tenant).order_by('display_name') if request.tenant else []
    return render(request, 'ai/providers.html', {'providers': providers})


# ─── Provider CRUD (Admin Only) ────────────────────────────────────


class AIProviderConfigForm(forms.ModelForm):
    models_list = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '{"gpt-4o": "GPT-4o", "gpt-3.5-turbo": "GPT-3.5"}'}),
        required=False,
        help_text="JSON com modelos disponíveis"
    )

    class Meta:
        model = AIProviderConfig
        fields = ['provider_name', 'display_name', 'models_list', 'is_default']

    def clean_models_list(self):
        import json
        val = self.cleaned_data.get('models_list', '')
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError("JSON inválido para modelos.")
        return {}


@login_required
def create_provider(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('ai:list')
    if request.method == 'POST':
        form = AIProviderConfigForm(request.POST)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.organization = request.tenant
            provider.save()
            messages.success(request, "Provedor criado com sucesso!")
            return redirect('ai:list')
    else:
        form = AIProviderConfigForm()
    return render(request, 'ai/provider_form.html', {'form': form})


@login_required
def edit_provider(request, pk):
    provider = get_object_or_404(AIProviderConfig, pk=pk)
    if request.method == 'POST':
        form = AIProviderConfigForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, "Provedor atualizado com sucesso!")
            return redirect('ai:list')
    else:
        form = AIProviderConfigForm(instance=provider)
    return render(request, 'ai/provider_form.html', {'form': form, 'object': provider})


@login_required
def delete_provider(request, pk):
    provider = get_object_or_404(AIProviderConfig, pk=pk)
    if request.method == 'POST':
        provider.delete()
        messages.success(request, "Provedor excluído com sucesso!")
        return redirect('ai:list')
    return render(request, 'ai/provider_confirm_delete.html', {
        'object': provider,
        'cancel_url': reverse('ai:list'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class AIProviderConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for AIProviderConfig model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["display_name"]
    ordering_fields = ["display_name", "provider_name", "is_default", "created_at"]

    def get_serializer_class(self):
        return AIProviderConfigSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_ai_provider_queryset(
            organization_id=org_id,
            provider_name=self.request.query_params.get("provider_name", type=int),
            is_default=self.request.query_params.get("is_default", type=str),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def set_default(self, request, pk=None):
        """Set this provider as the default."""
        provider = self.get_object()
        org_id = provider.organization_id
        if org_id:
            AIProviderConfig.objects.filter(
                organization_id=org_id
            ).update(is_default=False)
            provider.is_default = True
            provider.save(update_fields=["is_default"])
        serializer = self.get_serializer(provider)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def sync_models(self, request, pk=None):
        """Sync available models from this AI provider."""
        provider = self.get_object()
        try:
            from apps.ai.services import AIService
            result = AIService.sync_provider_models(provider)
            serializer = self.get_serializer(provider)
            return Response({"status": "synced", "provider": serializer.data})
        except Exception as e:
            logger.exception("Model sync failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIModelConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for AIModelConfig model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["model_id", "display_name"]
    ordering_fields = ["display_name", "model_id", "max_tokens", "created_at"]

    def get_serializer_class(self):
        return AIModelConfigSerializer

    def get_queryset(self):
        return get_ai_model_config_queryset(
            provider_id=self.request.query_params.get("provider_id", type=int),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        serializer.save()


class AICallLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AICallLog model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-created_at", "provider_name", "model", "cost"]

    def get_serializer_class(self):
        return AICallLogSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_ai_call_log_queryset(
            organization_id=org_id,
            user_id=self.request.query_params.get("user_id", type=int),
            provider_name=self.request.query_params.get("provider_name"),
            model=self.request.query_params.get("model"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get AI usage statistics."""
        qs = self.get_queryset()
        from django.db.models import Sum, Count, Avg
        stats = qs.aggregate(
            total_calls=Count("id"),
            total_tokens_input=Sum("tokens_input"),
            total_tokens_output=Sum("tokens_output"),
            total_cost=Sum("cost"),
            avg_latency_ms=Avg("latency_ms"),
        )
        return Response({"stats": stats})
