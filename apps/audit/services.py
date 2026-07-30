import logging
from apps.audit.models import AuditLog


logger = logging.getLogger(__name__)


class AuditService:
    """Service layer for audit log operations."""

    @staticmethod
    def log(
        action,
        target_type,
        target_id="",
        actor=None,
        actor_type="user",
        ip_address=None,
        user_agent="",
        metadata=None,
        organization=None,
    ):
        """Create an audit log entry."""
        AuditLog.objects.create(
            actor=actor,
            actor_type=actor_type,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            organization=organization,
        )

    @staticmethod
    def log_api_request(request, action, target_type, target_id="", metadata=None):
        """Convenience method to log an API request."""
        actor = request.user if request.user.is_authenticated else None
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        organization = getattr(request, "tenant", None)

        AuditService.log(
            action=action,
            target_type=target_type,
            target_id=target_id,
            actor=actor,
            actor_type="api",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
            organization=organization,
        )
