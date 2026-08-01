"""Endpoint /api/v1/team consumido pelo frontend (src/app/app/equipe/page.tsx).

Junta dois modelos do Core que já existiam sem view de API compatível:
Membership (membros ativos/suspensos) e Invitation (convites pendentes).
Reaproveita OrganizationService (invite_member/remove_member) em vez de
duplicar a lógica de convite.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.views import TenantAPIView
from apps.clients.models import Department
from apps.common.constants import MembershipRole, MembershipStatus, InvitationStatus
from apps.common.exceptions import ValidationError as ServiceValidationError, PermissionDeniedError, NotFoundException
from apps.organizations.models import Membership, Invitation
from apps.organizations.services import OrganizationService
from apps.audit.helpers import log_audit

ROLE_SLUGS = {
    MembershipRole.OWNER: "owner",
    MembershipRole.ADMIN: "admin",
    MembershipRole.MEMBER: "collaborator",
    MembershipRole.VIEWER: "viewer",
}
ROLE_SLUGS_REVERSE = {v: k for k, v in ROLE_SLUGS.items()}


def _serialize_membership(m):
    return {
        "id": f"m-{m.id}",
        "name": m.user.get_display_name(),
        "email": m.user.email,
        "role": ROLE_SLUGS.get(m.role, "collaborator"),
        "status": "suspended" if m.status == MembershipStatus.SUSPENDED else "active",
        "department_id": m.department_id,
        "business_unit_id": None,
        "last_access": m.user.last_login,
        "created_at": m.created_at,
        "department": (
            {"id": m.department_id, "name": m.department.name, "color": m.department.color}
            if m.department_id else None
        ),
        "business_unit": None,
        "user": {"id": m.user_id, "email": m.user.email, "avatar": m.user.avatar.url if m.user.avatar else None},
    }


def _serialize_invitation(inv):
    return {
        "id": f"i-{inv.id}",
        "name": inv.email.split("@")[0],
        "email": inv.email,
        "role": ROLE_SLUGS.get(inv.role, "collaborator"),
        "status": "invited",
        "department_id": None,
        "business_unit_id": None,
        "last_access": None,
        "created_at": inv.created_at,
        "department": None,
        "business_unit": None,
        "user": None,
    }


class OrganizationCreateView(APIView):
    """POST /api/v1/organizations/create — bootstrap para usuario autenticado
    sem nenhuma organizacao ainda (ex.: veio do fluxo de checkout, ou saiu da
    ultima org). Nao pode exigir request.tenant como TenantAPIView exige,
    pois e exatamente essa a organizacao que ainda nao existe."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response({"error": "Nome da organização é obrigatório."}, status=400)
        org = OrganizationService.create_organization(name=name, owner=request.user)
        return Response({"id": org.id, "name": org.name, "slug": org.slug}, status=201)


class CurrentOrganizationView(TenantAPIView):
    """GET/PUT /api/v1/organizations — nome da org (topbar) e, com
    ?include=subscription, os dados reais de assinatura usados por
    /app/assinatura (apps.billing: Plan/Subscription/Invoice)."""

    def get(self, request):
        org = request.tenant
        data = {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "membersCount": Membership.objects.filter(
                organization=org, status=MembershipStatus.ACTIVE
            ).count(),
        }
        if request.query_params.get("include") == "subscription":
            data["subscription"] = self._serialize_subscription(org)
        return Response(data)

    def put(self, request):
        from apps.billing.models import Plan
        from apps.common.constants import SubscriptionStatus

        subscription = self._current_subscription(request.tenant)
        if not subscription:
            return Response({"error": "Nenhuma assinatura ativa para esta organização."}, status=404)

        if "cancel" in request.data:
            subscription.cancel_at_period_end = bool(request.data["cancel"])
            subscription.save(update_fields=["cancel_at_period_end", "updated_at"])
        if request.data.get("plan_id"):
            plan = Plan.objects.filter(pk=request.data["plan_id"], is_active=True).first()
            if not plan:
                return Response({"error": "Plano inválido."}, status=400)
            subscription.plan = plan
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.save(update_fields=["plan", "status", "updated_at"])
            log_audit(request, action="plan_changed", target_type="subscription", target_id=subscription.id, metadata={"plan": plan.name})

        if "cancel" in request.data:
            action = "subscription_cancel_scheduled" if request.data["cancel"] else "subscription_reactivated"
            log_audit(request, action=action, target_type="subscription", target_id=subscription.id)

        return Response(self._serialize_subscription(request.tenant))

    def _current_subscription(self, org):
        from apps.billing.models import Subscription
        from apps.common.constants import SubscriptionStatus
        return (
            Subscription.objects.filter(
                organization=org,
                status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING, SubscriptionStatus.PAST_DUE],
            )
            .select_related("plan")
            .order_by("-created_at")
            .first()
        )

    def _serialize_subscription(self, org):
        from apps.common.constants import BillingCycle, SubscriptionStatus
        from apps.billing.api_views import serialize_plan
        from apps.clients.models import ClientCompany
        from apps.radar_documents.models import Document

        sub = self._current_subscription(org)
        if not sub:
            return None

        status_slugs = {
            SubscriptionStatus.ACTIVE: "active", SubscriptionStatus.TRIALING: "trialing",
            SubscriptionStatus.PAST_DUE: "past_due", SubscriptionStatus.CANCELED: "canceled",
            SubscriptionStatus.PAUSED: "paused", SubscriptionStatus.UNPAID: "unpaid",
        }
        cycle_slugs = {
            BillingCycle.ANNUAL: "annual", BillingCycle.SEMIANNUAL: "semiannual",
            BillingCycle.QUARTERLY: "quarterly", BillingCycle.MONTHLY: "monthly",
        }

        return {
            "id": sub.id,
            "plan_id": sub.plan_id,
            "status": status_slugs.get(sub.status, "active"),
            "billing_cycle": cycle_slugs.get(sub.plan.billing_cycle, "monthly"),
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "plan": serialize_plan(sub.plan, current_plan_id=sub.plan_id),
            "organization": {
                "count": {
                    "clients": ClientCompany.objects.filter(organization=org, is_deleted=False).count(),
                    "members": Membership.objects.filter(organization=org, status=MembershipStatus.ACTIVE).count(),
                    "documents": Document.objects.filter(organization=org).count(),
                }
            },
        }


class TeamView(TenantAPIView):
    def get(self, request):
        if request.query_params.get("include") == "departments":
            return self._get_departments(request)
        return self._get_members(request)

    def _get_members(self, request):
        org = request.tenant
        memberships = (
            Membership.objects.filter(
                organization=org,
                status__in=[MembershipStatus.ACTIVE, MembershipStatus.SUSPENDED],
            )
            .select_related("user", "department")
            .order_by("-created_at")
        )
        invitations = Invitation.objects.filter(
            organization=org, status=InvitationStatus.PENDING
        ).order_by("-created_at")

        data = [_serialize_membership(m) for m in memberships]
        data += [_serialize_invitation(i) for i in invitations]
        return Response(data)

    def _get_departments(self, request):
        departments = Department.objects.filter(organization=request.tenant).order_by("name")
        data = [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "color": d.color,
                "manager_id": d.manager_id,
                "count": {"members": d.members.count(), "templates": d.templates.count()},
            }
            for d in departments
        ]
        return Response(data)

    def post(self, request):
        org = request.tenant
        name = (request.data.get("name") or "").strip()
        email = (request.data.get("email") or "").strip().lower()
        role_slug = request.data.get("role") or "collaborator"

        if not name or not email:
            return Response({"error": "Nome e e-mail são obrigatórios."}, status=400)

        if Membership.objects.filter(
            organization=org, user__email__iexact=email, status=MembershipStatus.ACTIVE
        ).exists():
            return Response({"error": "Este e-mail já é membro da organização."}, status=409)
        if Invitation.objects.filter(
            organization=org, email__iexact=email, status=InvitationStatus.PENDING
        ).exists():
            return Response({"error": "Já existe um convite pendente para este e-mail."}, status=409)

        role = ROLE_SLUGS_REVERSE.get(role_slug, MembershipRole.MEMBER)
        try:
            invitation = OrganizationService.invite_member(org, email, role, invited_by=request.user)
        except ServiceValidationError as e:
            return Response({"error": str(e)}, status=400)

        _send_invite_email(invitation, org, name)
        log_audit(request, action="member_invited", target_type="invitation", target_id=invitation.id, metadata={"email": email})
        return Response(_serialize_invitation(invitation), status=201)

    def put(self, request):
        raw_id = str(request.data.get("id") or "")
        new_status = request.data.get("status")
        if "-" not in raw_id:
            return Response({"error": "id inválido."}, status=400)
        kind, _, obj_id = raw_id.partition("-")

        if kind == "i":
            return self._put_invitation(request, obj_id, new_status)
        if kind == "m":
            return self._put_membership(request, obj_id, new_status)
        return Response({"error": "id inválido."}, status=400)

    def _put_invitation(self, request, obj_id, new_status):
        invitation = Invitation.objects.filter(
            id=obj_id, organization=request.tenant, status=InvitationStatus.PENDING
        ).first()
        if not invitation:
            return Response({"error": "Convite não encontrado."}, status=404)

        if new_status == "removed":
            invitation.status = InvitationStatus.DECLINED
            invitation.save(update_fields=["status", "updated_at"])
            return Response({"success": True})

        # "invited" (reenviar): renova validade e reenvia o e-mail.
        from datetime import timedelta
        from django.utils import timezone
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.save(update_fields=["expires_at", "updated_at"])
        _send_invite_email(invitation, request.tenant, invitation.email.split("@")[0])
        return Response(_serialize_invitation(invitation))

    def _put_membership(self, request, obj_id, new_status):
        membership = Membership.objects.filter(
            id=obj_id, organization=request.tenant
        ).select_related("user").first()
        if not membership:
            return Response({"error": "Membro não encontrado."}, status=404)

        if new_status == "removed":
            try:
                OrganizationService.remove_member(request.tenant, membership.user, removed_by=request.user)
            except PermissionDeniedError as e:
                return Response({"error": str(e)}, status=403)
            except NotFoundException as e:
                return Response({"error": str(e)}, status=404)
            log_audit(request, action="member_removed", target_type="membership", target_id=membership.id, metadata={"email": membership.user.email})
            return Response({"success": True})

        if new_status == "suspended":
            if membership.user_id == request.tenant.owner_id:
                return Response({"error": "Não é possível suspender o proprietário."}, status=403)
            membership.status = MembershipStatus.SUSPENDED
            membership.save(update_fields=["status", "updated_at"])
            log_audit(request, action="member_suspended", target_type="membership", target_id=membership.id, metadata={"email": membership.user.email})
        elif new_status == "active":
            membership.status = MembershipStatus.ACTIVE
            membership.save(update_fields=["status", "updated_at"])
            log_audit(request, action="member_reactivated", target_type="membership", target_id=membership.id, metadata={"email": membership.user.email})
        else:
            return Response({"error": "Status inválido."}, status=400)

        return Response(_serialize_membership(membership))


def _send_invite_email(invitation, org, invitee_name):
    """Best-effort — não deve derrubar o convite se o envio falhar."""
    try:
        from apps.notifications.services import NotificationService
        NotificationService.send_notification(
            channel="email",
            recipient=invitation.email,
            template_code="team_invite",
            context={
                "name": invitee_name,
                "organization": org.name,
                "token": str(invitation.token),
            },
        )
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Falha ao enviar e-mail de convite para %s", invitation.email, exc_info=True)
