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

from apps.organizations.models import Organization, Membership, Invitation
from apps.organizations.serializers import (
    OrganizationSerializer,
    OrganizationListSerializer,
    MembershipSerializer,
    InvitationSerializer,
    InvitationCreateSerializer,
)
from apps.organizations.services import OrganizationService
from apps.organizations.selectors import (
    get_organization_list_queryset,
    get_membership_queryset,
    get_invitation_queryset,
    get_user_organizations,
    get_organization_members,
    get_pending_invitations,
)
from apps.common.constants import MembershipRole, MembershipStatus

logger = logging.getLogger(__name__)

app_name = "organizations"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_organizations(request):
    orgs = get_user_organizations(request.user.id)
    return render(request, "organizations/list.html", {"organizations": orgs})


@login_required
def create_organization(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            org = OrganizationService.create_organization(name=name, owner=request.user)
            return redirect("organizations:detail", org_id=org.id)
    return render(request, "organizations/create.html")


@login_required
def detail_organization(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    members = get_organization_members(org_id)
    invitations = get_pending_invitations(org_id)
    return render(request, "organizations/detail.html", {"organization": org, "members": members, "invitations": invitations})


@login_required
def edit_organization(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        status_val = int(request.POST.get('status', MembershipStatus.ACTIVE))
        if name:
            org.name = name
            org.status = status_val
            org.save(update_fields=['name', 'status', 'updated_at'])
            messages.success(request, "Organização atualizada com sucesso!")
            return redirect('organizations:detail', org_id=org.id)
    return render(request, 'organizations/edit.html', {'organization': org})


@login_required
def delete_organization(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    if request.method == 'POST':
        org.delete()
        messages.success(request, "Organização excluída com sucesso!")
        return redirect('organizations:list')
    return render(request, 'organizations/confirm_delete.html', {
        'object': org,
        'cancel_url': reverse('organizations:detail', args=[org_id]),
    })


@login_required
def switch_organization(request):
    if request.GET.get("org_id"):
        request.session["active_organization_id"] = request.GET["org_id"]
    from django.http import HttpResponse
    return HttpResponse("")


@login_required
def invite_member(request):
    if request.method == "POST":
        org_id = request.POST.get("organization_id")
        email = request.POST.get("email", "").strip()
        role = int(request.POST.get("role", 3))
        org = get_object_or_404(Organization, id=org_id)
        try:
            OrganizationService.invite_member(org, email, role, invited_by=request.user)
        except Exception:
            pass
        return redirect("organizations:detail", org_id=org_id)
    return render(request, "organizations/invite.html")


# ─── DRF API ViewSets ───────────────────────────────────────────────


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model."""

    queryset = Organization.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at", "status"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrganizationListSerializer
        return OrganizationSerializer

    def get_queryset(self):
        return get_organization_list_queryset()

    def perform_create(self, serializer):
        org = OrganizationService.create_organization(
            name=serializer.validated_data["name"],
            owner=self.request.user,
            metadata=serializer.validated_data.get("metadata", {}),
        )
        serializer.instance = org

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def members(self, request, pk=None):
        """Get all members of an organization."""
        from apps.organizations.serializers import MembershipSerializer
        members = get_organization_members(pk)
        serializer = MembershipSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def invitations(self, request, pk=None):
        """Get pending invitations for an organization."""
        invitations = get_pending_invitations(pk)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)


class MembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for Membership model."""

    queryset = Membership.objects.select_related("user", "organization", "invited_by")
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["role", "status", "created_at"]

    def get_queryset(self):
        return get_membership_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            user_id=self.request.query_params.get("user_id"),
            status=self.request.query_params.get("status"),
            role=self.request.query_params.get("role"),
        )

    def perform_create(self, serializer):
        """Prevent manual creation - use invite flow instead."""
        from rest_framework.exceptions import MethodNotAllowed
        raise MethodNotAllowed("POST", detail="Use the invitation flow to add members.")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def update_role(self, request, pk=None):
        """Update a member's role."""
        membership = self.get_object()
        new_role = request.data.get("role")
        if new_role is None:
            return Response(
                {"error": "Role field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            updated = OrganizationService.update_member_role(
                organization=membership.organization,
                user=membership.user,
                new_role=int(new_role),
            )
            serializer = self.get_serializer(updated)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for Invitation model."""

    queryset = Invitation.objects.select_related("organization", "invited_by")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email"]
    ordering_fields = ["created_at", "status", "expires_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return InvitationCreateSerializer
        return InvitationSerializer

    def get_queryset(self):
        return get_invitation_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            email=self.request.query_params.get("email"),
            status=self.request.query_params.get("status"),
        )

    def perform_create(self, serializer):
        invitation = OrganizationService.invite_member(
            organization=serializer.validated_data["organization"],
            email=serializer.validated_data["email"],
            role=serializer.validated_data.get("role", MembershipRole.MEMBER),
            invited_by=self.request.user,
        )
        serializer.instance = invitation

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """Accept an invitation."""
        invitation = self.get_object()
        try:
            membership = OrganizationService.accept_invitation(invitation, request.user)
            from apps.organizations.serializers import MembershipSerializer
            serializer = MembershipSerializer(membership)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def decline(self, request, pk=None):
        """Decline an invitation."""
        invitation = self.get_object()
        try:
            OrganizationService.decline_invitation(invitation)
            return Response({"status": "declined"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
