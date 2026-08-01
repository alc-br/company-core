"""JSON auth endpoints consumed by the Next.js frontend proxy.

The frontend (company-radar) posts to /api/auth/register and /api/auth/login
expecting JSON in/out and a session cookie, not allauth's classic HTML views
(mounted separately under /account/). See src/app/(public)/login/page.tsx and
src/app/(public)/register/page.tsx and src/app/api/auth/[...path]/route.ts in
the company-radar repo for the exact contract these views satisfy.
"""
import json
import logging

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.common.constants import MembershipRole, MembershipStatus
from apps.organizations.models import Membership
from apps.organizations.services import OrganizationService
from apps.users.models import CustomUser

logger = logging.getLogger(__name__)

ROLE_SLUGS = {
    MembershipRole.OWNER: "owner",
    MembershipRole.ADMIN: "admin",
    MembershipRole.MEMBER: "collaborator",
    MembershipRole.VIEWER: "viewer",
}


def _parse_json(request):
    try:
        return json.loads(request.body or b"{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON invalido."}, status=400)


def _serialize_user(user):
    memberships = (
        Membership.objects.filter(user=user, status=MembershipStatus.ACTIVE)
        .select_related("organization")
        .order_by("-created_at")
    )
    membership_list = []
    active_org = None
    for m in memberships:
        membership_list.append({
            "organizationId": str(m.organization_id),
            "role": ROLE_SLUGS.get(m.role, "collaborator"),
        })
        if active_org is None:
            active_org = {
                "id": str(m.organization_id),
                "name": m.organization.name,
                "slug": m.organization.slug,
            }
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.get_display_name(),
        "activeOrg": active_org,
        "memberships": membership_list,
    }


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    data, error = _parse_json(request)
    if error:
        return error

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    first_name = (data.get("name") or "").strip()
    last_name = (data.get("lastName") or "").strip()

    if not email or not password:
        return JsonResponse({"error": "E-mail e senha sao obrigatorios."}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "A senha deve ter no minimo 8 caracteres."}, status=400)
    if CustomUser.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Este e-mail ja esta cadastrado."}, status=409)

    org_label = f"{first_name} {last_name}".strip() or email.split("@")[0]

    try:
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            OrganizationService.create_organization(
                name=f"Escritório de {org_label}",
                owner=user,
            )
    except IntegrityError:
        return JsonResponse({"error": "Este e-mail ja esta cadastrado."}, status=409)

    logger.info(f"New account registered: {user.email} (id={user.id})")
    return JsonResponse({"success": True}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    data, error = _parse_json(request)
    if error:
        return error

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = authenticate(request, username=email, password=password)
    if user is None or not user.is_active:
        return JsonResponse({"error": "E-mail ou senha invalidos."}, status=401)

    auth_login(request, user)
    try:
        from apps.audit.helpers import log_audit
        from apps.organizations.models import Membership
        from apps.common.constants import MembershipStatus
        active = Membership.objects.filter(user=user, status=MembershipStatus.ACTIVE).select_related("organization").first()
        request.tenant = active.organization if active else None
        log_audit(request, action="login", target_type="user", target_id=user.id)
    except Exception:
        pass
    return JsonResponse({"user": _serialize_user(user)})


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    auth_logout(request)
    return JsonResponse({"success": True})
