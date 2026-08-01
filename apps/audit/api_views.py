"""Endpoint /api/v1/audit consumido pela aba Auditoria de /app/configuracoes."""
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.audit.models import AuditLog
from apps.audit.helpers import log_audit


class AuditListView(TenantAPIView):
    def post(self, request):
        """Usado pela aba Dados e Privacidade: registra solicitacoes de
        exportacao/LGPD como um evento de auditoria real e rastreavel,
        em vez de so mostrar um toast que nao fica registrado em lugar algum."""
        action = request.data.get("action")
        if action not in ("data_export_requested", "lgpd_request"):
            return Response({"error": "Ação inválida."}, status=400)
        log_audit(request, action=action, target_type="organization", target_id=request.tenant.id)
        return Response({"success": True}, status=201)

    def get(self, request):
        qp = request.query_params
        qs = AuditLog.objects.filter(organization=request.tenant).select_related("actor")

        if qp.get("action"):
            qs = qs.filter(action__icontains=qp["action"])

        total = qs.count()
        page = max(int(qp.get("page", 1)), 1)
        limit = min(int(qp.get("limit", 20)), 100)
        start = (page - 1) * limit
        rows = qs.order_by("-created_at")[start:start + limit]

        logs = [
            {
                "id": row.id,
                "user_name": row.actor.get_display_name() if row.actor_id else None,
                "action": row.action,
                "entity": row.target_type or None,
                "entity_id": row.target_id or None,
                "detail": ", ".join(f"{k}={v}" for k, v in (row.metadata or {}).items()) or None,
                "ip": row.ip_address,
                "created_at": row.created_at,
            }
            for row in rows
        ]
        return Response({"logs": logs, "total": total})
