"""Endpoint /api/v1/notifications consumido pelo frontend (topbar + /app/notificacoes).

Inbox in-app real, por usuario/organizacao. Distinto do NotificationLog
(que so registra tentativas de envio por e-mail em apps/notifications/services.py).
"""
from django.utils import timezone
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.notifications.models import Notification


def notify_user(organization, user, title, message, type="info", priority="normal", link=""):
    """Cria uma notificacao in-app real. Best-effort: nunca derruba o fluxo que a originou."""
    if not user or not organization:
        return None
    try:
        return Notification.objects.create(
            organization=organization, user=user, title=title, message=message,
            type=type, priority=priority, link=link,
        )
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Falha ao criar notificacao para user=%s", user, exc_info=True)
        return None


def _serialize(n):
    return {
        "id": str(n.id),
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "priority": n.priority,
        "link": n.link or None,
        "read": n.read,
        "read_at": n.read_at,
        "created_at": n.created_at,
    }


class NotificationListView(TenantAPIView):
    def get(self, request):
        qs = Notification.objects.filter(organization=request.tenant, user=request.user)
        notif_type = request.query_params.get("type")
        if notif_type and notif_type != "all":
            qs = qs.filter(type=notif_type)
        qs = qs.order_by("-created_at")[:200]

        unread = Notification.objects.filter(
            organization=request.tenant, user=request.user, read=False
        ).count()

        return Response({
            "unread": unread,
            "notifications": [_serialize(n) for n in qs],
        })

    def put(self, request):
        ids = request.data.get("ids") or []
        if not ids:
            return Response({"error": "ids é obrigatório."}, status=400)
        updated = Notification.objects.filter(
            organization=request.tenant, user=request.user, id__in=ids, read=False
        ).update(read=True, read_at=timezone.now())
        return Response({"success": True, "updated": updated})
