import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.users.models import CustomUser
from apps.users.serializers import (
    CustomUserSerializer,
    CustomUserListSerializer,
    CustomUserUpdateSerializer,
    CustomUserAdminSerializer,
)
from apps.users.services import UserService
from apps.users.selectors import (
    get_user_queryset,
    get_tenant_users_queryset,
)

logger = logging.getLogger(__name__)

app_name = "users"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def profile_view(request):
    """User profile view."""
    return render(request, "users/profile.html", {"user": request.user})


@login_required
def profile_edit_view(request):
    """User profile edit view."""
    if request.method == "POST":
        form_data = request.POST
        request.user.first_name = form_data.get("first_name", "")
        request.user.last_name = form_data.get("last_name", "")
        request.user.bio = form_data.get("bio", "")
        request.user.timezone = form_data.get("timezone", "America/Sao_Paulo")
        request.user.save()
        return redirect("users:profile")
    return render(request, "users/profile_edit.html", {"user": request.user})


# ─── DRF API ViewSets ───────────────────────────────────────────────


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for CustomUser model."""

    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "first_name", "last_name", "date_joined", "is_active"]

    def get_serializer_class(self):
        if self.action == "list":
            return CustomUserListSerializer
        if self.action in ("update", "partial_update"):
            if self.request.user.is_staff:
                return CustomUserAdminSerializer
            return CustomUserUpdateSerializer
        return CustomUserSerializer

    def get_queryset(self):
        # Regular users can only see users in their organization
        if not self.request.user.is_staff:
            organization_id = self.request.query_params.get("organization_id")
            tenant = getattr(self.request, "tenant", None)
            if organization_id:
                return get_tenant_users_queryset(int(organization_id))
            elif tenant:
                return get_tenant_users_queryset(tenant.id)
            else:
                # Only return the current user
                return CustomUser.objects.filter(id=self.request.user.id)
        return get_user_queryset(
            is_active=self.request.query_params.get("is_active"),
            is_staff=self.request.query_params.get("is_staff"),
        )

    def get_permissions(self):
        """Only admin users can create/delete users."""
        if self.action in ("create", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_object(self):
        """Allow users to access their own profile via /users/me/."""
        if self.kwargs.get("pk") == "me":
            self.kwargs["pk"] = self.request.user.pk
        return super().get_object()

    def perform_update(self, serializer):
        user = serializer.instance
        if self.request.user == user or self.request.user.is_staff:
            UserService.update_profile(user, **serializer.validated_data)
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot update another user's profile.")

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get the current authenticated user's profile."""
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a user account."""
        user = self.get_object()
        UserService.deactivate_user(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """Activate a user account."""
        user = self.get_object()
        UserService.activate_user(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
