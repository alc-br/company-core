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

from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment
from apps.feature_flags.serializers import (
    FeatureFlagSerializer,
    FeatureFlagListSerializer,
    FeatureFlagAssignmentSerializer,
)
from apps.feature_flags.services import FeatureFlagService
from apps.feature_flags.selectors import (
    get_feature_flag_queryset,
    get_feature_flag_assignment_queryset,
    is_flag_active_for_organization,
    is_flag_active_for_user,
)

logger = logging.getLogger(__name__)

app_name = "feature_flags"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_flags(request):
    flags = FeatureFlag.objects.all()
    return render(request, "feature_flags/list.html", {"flags": flags})


# ─── FeatureFlag CRUD Template Views (Admin Only) ──────────────────


class FeatureFlagForm(forms.ModelForm):
    class Meta:
        model = FeatureFlag
        fields = ['code', 'name', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['code'].widget.attrs['readonly'] = True


@login_required
def create_flag(request):
    if request.method == 'POST':
        form = FeatureFlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.created_by = request.user
            flag.save()
            messages.success(request, "Feature flag criada com sucesso!")
            return redirect('feature_flags:list')
    else:
        form = FeatureFlagForm()
    return render(request, 'feature_flags/flag_form.html', {'form': form})


@login_required
def edit_flag(request, pk):
    flag = get_object_or_404(FeatureFlag, pk=pk)
    if request.method == 'POST':
        form = FeatureFlagForm(request.POST, instance=flag)
        if form.is_valid():
            form.save()
            messages.success(request, "Feature flag atualizada com sucesso!")
            return redirect('feature_flags:list')
    else:
        form = FeatureFlagForm(instance=flag)
    return render(request, 'feature_flags/flag_form.html', {'form': form, 'object': flag})


@login_required
def toggle_flag(request, pk):
    flag = get_object_or_404(FeatureFlag, pk=pk)
    flag.is_active = not flag.is_active
    flag.save(update_fields=['is_active', 'updated_at'])
    status_text = "ativada" if flag.is_active else "desativada"
    messages.success(request, f"Feature flag {status_text} com sucesso!")
    return redirect('feature_flags:list')


@login_required
def delete_flag(request, pk):
    flag = get_object_or_404(FeatureFlag, pk=pk)
    if request.method == 'POST':
        flag.delete()
        messages.success(request, "Feature flag excluída com sucesso!")
        return redirect('feature_flags:list')
    return render(request, 'feature_flags/flag_confirm_delete.html', {
        'object': flag,
        'cancel_url': reverse('feature_flags:list'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class FeatureFlagViewSet(viewsets.ModelViewSet):
    """ViewSet for FeatureFlag model. Admin-only for create/update/delete."""

    queryset = FeatureFlag.objects.select_related("created_by")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "is_active", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return FeatureFlagListSerializer
        return FeatureFlagSerializer

    def get_queryset(self):
        return get_feature_flag_queryset(
            is_active=self.request.query_params.get("is_active"),
            code=self.request.query_params.get("code"),
        )

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        flag = FeatureFlagService.create_flag(
            code=serializer.validated_data["code"],
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            created_by=self.request.user,
            is_active=serializer.validated_data.get("is_active", False),
        )
        serializer.instance = flag

    def perform_update(self, serializer):
        flag = serializer.instance
        FeatureFlagService.update_flag(
            flag,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
            is_active=serializer.validated_data.get("is_active"),
        )
        serializer.instance = flag

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def toggle(self, request, pk=None):
        """Toggle a feature flag's active state."""
        flag = self.get_object()
        toggled = FeatureFlagService.toggle_flag(flag)
        serializer = self.get_serializer(toggled)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def check(self, request):
        """Check if a feature flag is active for the current context."""
        code = request.query_params.get("code")
        if not code:
            return Response(
                {"error": "code query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for organization
        organization_id = request.query_params.get("organization_id")
        if organization_id:
            is_active = is_flag_active_for_organization(code, int(organization_id))
            return Response({"code": code, "organization_id": organization_id, "is_active": is_active})

        # Check for user
        user_id = request.query_params.get("user_id")
        if user_id:
            is_active = is_flag_active_for_user(code, int(user_id))
            return Response({"code": code, "user_id": user_id, "is_active": is_active})

        # Check global state
        from apps.feature_flags.models import FeatureFlag
        flag = FeatureFlag.objects.filter(code=code).first()
        if not flag:
            return Response({"code": code, "is_active": False}, status=status.HTTP_404_NOT_FOUND)
        return Response({"code": code, "is_active": flag.is_active})


class FeatureFlagAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for FeatureFlagAssignment model."""

    queryset = FeatureFlagAssignment.objects.select_related("flag", "organization", "user")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "is_active", "environment"]

    def get_serializer_class(self):
        return FeatureFlagAssignmentSerializer

    def get_queryset(self):
        return get_feature_flag_assignment_queryset(
            flag_id=self.request.query_params.get("flag_id"),
            organization_id=self.request.query_params.get("organization_id"),
            user_id=self.request.query_params.get("user_id"),
            environment=self.request.query_params.get("environment"),
            is_active=self.request.query_params.get("is_active"),
        )

    def perform_create(self, serializer):
        flag = serializer.validated_data["flag"]
        organization = serializer.validated_data.get("organization")
        user = serializer.validated_data.get("user")
        environment = serializer.validated_data.get("environment", "production")
        is_active = serializer.validated_data.get("is_active", True)

        if organization:
            assignment = FeatureFlagService.assign_flag_to_organization(
                flag=flag, organization=organization,
                environment=environment, is_active=is_active,
            )
        elif user:
            assignment = FeatureFlagService.assign_flag_to_user(
                flag=flag, user=user,
                environment=environment, is_active=is_active,
            )
        else:
            return Response(
                {"error": "Either organization or user must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.instance = assignment
