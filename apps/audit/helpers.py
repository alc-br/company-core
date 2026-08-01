"""Helper para gravar entradas reais de auditoria a partir de qualquer view.

Best-effort: nunca deve derrubar a acao que a originou.
"""
import logging

logger = logging.getLogger(__name__)


def log_audit(request, action, target_type, target_id="", metadata=None):
    from apps.audit.models import AuditLog

    try:
        AuditLog.objects.create(
            actor=request.user if getattr(request.user, "is_authenticated", False) else None,
            action=action,
            target_type=target_type,
            target_id=str(target_id or ""),
            ip_address=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
            metadata=metadata or {},
            organization=getattr(request, "tenant", None),
        )
    except Exception:
        logger.warning("Falha ao gravar audit log: action=%s", action, exc_info=True)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
