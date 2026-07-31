import logging

from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.clients.models import ClientContact
from apps.radar_portal.models import Announcement

logger = logging.getLogger(__name__)


def _get_portal_contact(request):
    contact_id = request.session.get("portal_contact_id")
    if not contact_id:
        return None
    return ClientContact.objects.filter(pk=contact_id, has_portal_access=True).select_related("client").first()


@csrf_exempt
@require_http_methods(["POST"])
def portal_login(request):
    import json
    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido."}, status=400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    contact = ClientContact.objects.filter(email__iexact=email, has_portal_access=True).select_related("client").first()
    if not contact or not contact.password_hash or not check_password(password, contact.password_hash):
        return JsonResponse({"error": "E-mail ou senha invalidos."}, status=401)

    request.session["portal_contact_id"] = contact.id
    return JsonResponse({
        "contactId": contact.id, "clientId": contact.client_id, "clientName": contact.client.name,
        "contactName": contact.name, "contactEmail": contact.email, "contactPhone": contact.phone,
    })


@csrf_exempt
@require_http_methods(["POST"])
def portal_logout(request):
    request.session.pop("portal_contact_id", None)
    return JsonResponse({"success": True})


class PortalMeView(APIView):
    permission_classes = [AllowAny]
    versioning_class = None

    def get(self, request):
        contact = _get_portal_contact(request)
        if not contact:
            return Response({"error": "Sessao do portal invalida."}, status=401)
        return Response({
            "contact_id": contact.id, "client_id": contact.client_id, "client_name": contact.client.name,
            "contact_name": contact.name, "contact_email": contact.email, "contact_phone": contact.phone,
        })


class AnnouncementListView(APIView):
    """Comunicados visiveis ao cliente autenticado no portal.

    O cliente vem sempre da sessao do contato (nunca do query param clientId
    que o frontend eventualmente manda) para nao vazar dados entre clientes.
    """
    permission_classes = [AllowAny]
    versioning_class = None

    def get(self, request):
        contact = _get_portal_contact(request)
        if not contact:
            return Response({"error": "Sessao do portal invalida."}, status=401)

        skip = int(request.query_params.get("skip", 0) or 0)
        take = int(request.query_params.get("take", 10) or 10)

        qs = Announcement.objects.filter(
            organization=contact.client.organization,
        ).filter(
            Q(clients__isnull=True) | Q(clients=contact.client)
        ).order_by("-published_at")[skip: skip + take]

        return Response([
            {"id": a.id, "title": a.title, "body": a.body, "author": a.author.get_display_name() if a.author_id else None, "published_at": a.published_at}
            for a in qs
        ])
