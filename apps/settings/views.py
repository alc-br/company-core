import logging
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.settings.models import TenantSetting, GlobalSetting
from apps.settings.serializers import (
    TenantSettingSerializer,
    TenantSettingUpdateSerializer,
    GlobalSettingSerializer,
)
from apps.settings.services import SettingsService
from apps.settings.selectors import (
    get_tenant_setting_queryset,
    get_global_setting_queryset,
)

logger = logging.getLogger(__name__)

app_name = "settings"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def view_settings(request):
    if not request.tenant:
        return render(request, "settings/view.html", {"settings": []})
    settings_list = TenantSetting.objects.filter(organization=request.tenant)
    return render(request, "settings/view.html", {"settings": settings_list})


@login_required
def edit_setting(request, pk):
    setting = get_object_or_404(TenantSetting, pk=pk)
    if request.method == 'POST':
        value = request.POST.get('value', '')
        environment = request.POST.get('environment', setting.environment)
        try:
            SettingsService.set(
                organization=setting.organization,
                key=setting.key,
                value=value,
                environment=environment,
            )
            messages.success(request, "Configuração atualizada com sucesso!")
            return redirect('settings:view')
        except Exception as e:
            messages.error(request, f"Erro ao atualizar: {str(e)}")
    return render(request, 'settings/edit.html', {'setting': setting})


# ─── DRF API ViewSets ───────────────────────────────────────────────


class TenantSettingViewSet(viewsets.ModelViewSet):
    """ViewSet for TenantSetting model."""

    queryset = TenantSetting.objects.select_related("organization")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["key"]
    ordering_fields = ["key", "environment", "created_at"]

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return TenantSettingUpdateSerializer
        return TenantSettingSerializer

    def get_queryset(self):
        return get_tenant_setting_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            key=self.request.query_params.get("key"),
            environment=self.request.query_params.get("environment"),
        )

    def perform_create(self, serializer):
        setting = SettingsService.set(
            organization=serializer.validated_data["organization"],
            key=serializer.validated_data["key"],
            value=serializer.validated_data["value"],
            environment=serializer.validated_data.get("environment", "production"),
        )
        serializer.instance = setting

    def perform_update(self, serializer):
        setting = serializer.instance
        SettingsService.set(
            organization=setting.organization,
            key=setting.key,
            value=serializer.validated_data.get("value", setting.value),
            environment=setting.environment,
        )
        serializer.instance = setting

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_value(self, request):
        """Get a single setting value by key."""
        organization_id = request.query_params.get("organization_id")
        key = request.query_params.get("key")
        environment = request.query_params.get("environment", "production")

        if not organization_id or not key:
            return Response(
                {"error": "organization_id and key query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.organizations.models import Organization
        try:
            org = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        value = SettingsService.get(org, key, default=None, environment=environment)
        return Response({
            "organization_id": organization_id,
            "key": key,
            "environment": environment,
            "value": value,
        })


class GlobalSettingViewSet(viewsets.ModelViewSet):
    """ViewSet for GlobalSetting model. Admin-only for create/update/delete."""

    queryset = GlobalSetting.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["key"]
    ordering_fields = ["key"]

    def get_serializer_class(self):
        return GlobalSettingSerializer

    def get_queryset(self):
        return get_global_setting_queryset(
            key=self.request.query_params.get("key"),
        )

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        setting = SettingsService.set_global(
            key=serializer.validated_data["key"],
            value=serializer.validated_data["value"],
            description=serializer.validated_data.get("description", ""),
        )
        serializer.instance = setting

    def perform_update(self, serializer):
        setting = serializer.instance
        SettingsService.set_global(
            key=setting.key,
            value=serializer.validated_data.get("value", setting.value),
            description=serializer.validated_data.get("description", ""),
        )
        serializer.instance = setting
