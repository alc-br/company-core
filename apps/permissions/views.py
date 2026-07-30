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

from apps.permissions.models import Permission, Role, RolePermission
from apps.permissions.serializers import (
    PermissionSerializer,
    RoleSerializer,
    RoleListSerializer,
    RolePermissionSerializer,
)
from apps.permissions.services import PermissionService
from apps.permissions.selectors import (
    get_permission_queryset,
    get_role_queryset,
    get_role_permission_queryset,
)

logger = logging.getLogger(__name__)

app_name = "permissions"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_permissions(request):
    permissions_list = Permission.objects.all()
    return render(request, "permissions/list.html", {"permissions": permissions_list})


@login_required
def list_roles(request):
    roles = Role.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "permissions/roles.html", {"roles": roles})


# ─── Role CRUD Template Views ────────────────────────────────────────


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'is_default', 'permissions']
        widgets = {
            'permissions': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].required = False


@login_required
def create_role(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('permissions:roles')
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.organization = request.tenant
            role.save()
            form.save_m2m()
            messages.success(request, "Papel criado com sucesso!")
            return redirect('permissions:roles')
    else:
        form = RoleForm()
    return render(request, 'permissions/role_form.html', {'form': form})


@login_required
def edit_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Papel atualizado com sucesso!")
            return redirect('permissions:roles')
    else:
        form = RoleForm(instance=role)
    return render(request, 'permissions/role_form.html', {'form': form, 'object': role})


@login_required
def delete_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, "Papel excluído com sucesso!")
        return redirect('permissions:roles')
    return render(request, 'permissions/role_confirm_delete.html', {
        'object': role,
        'cancel_url': reverse('permissions:roles'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Permission model (read-only)."""

    queryset = Permission.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["module", "code", "name"]

    def get_serializer_class(self):
        return PermissionSerializer

    def get_queryset(self):
        return get_permission_queryset(
            code=self.request.query_params.get("code"),
            module=self.request.query_params.get("module"),
        )


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role model."""

    queryset = Role.objects.select_related("organization").prefetch_related("permissions")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "is_default"]

    def get_serializer_class(self):
        if self.action == "list":
            return RoleListSerializer
        return RoleSerializer

    def get_queryset(self):
        return get_role_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            is_default=self.request.query_params.get("is_default"),
        )

    def perform_create(self, serializer):
        role = PermissionService.create_role(
            organization=serializer.validated_data["organization"],
            name=serializer.validated_data["name"],
            permission_codes=serializer.validated_data.get("permission_codes", []),
            is_default=serializer.validated_data.get("is_default", False),
        )
        serializer.instance = role

    def perform_update(self, serializer):
        role = serializer.instance
        PermissionService.update_role(
            role=role,
            name=serializer.validated_data.get("name"),
            is_default=serializer.validated_data.get("is_default"),
            permission_codes=serializer.validated_data.get("permission_codes"),
        )
        serializer.instance = role

    def perform_destroy(self, instance):
        PermissionService.delete_role(instance)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_permission(self, request, pk=None):
        """Add a permission to a role."""
        role = self.get_object()
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return Response(
                {"error": "permission_code field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            rp = PermissionService.add_permission_to_role(role, permission_code)
            serializer = RolePermissionSerializer(rp)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def remove_permission(self, request, pk=None):
        """Remove a permission from a role."""
        role = self.get_object()
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return Response(
                {"error": "permission_code field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            deleted = PermissionService.remove_permission_from_role(role, permission_code)
            return Response({"deleted_count": deleted[0]})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RolePermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for RolePermission through model."""

    queryset = RolePermission.objects.select_related("role", "permission")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]

    def get_serializer_class(self):
        return RolePermissionSerializer

    def get_queryset(self):
        return get_role_permission_queryset(
            role_id=self.request.query_params.get("role_id"),
        )
