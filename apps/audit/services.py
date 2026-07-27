import logging
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
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
