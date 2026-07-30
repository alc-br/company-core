import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_audit_logs_task(self, days=180):
    """Archive and clean up old audit logs."""
    from apps.audit.models import AuditLog

    try:
        cutoff = timezone.now() - timedelta(days=days)
        logs = AuditLog.objects.filter(created_at__lt=cutoff)

        count = logs.count()
        if count > 0:
            # Log summary before deletion for audit trail
            logger.info(
                f"Archiving {count} audit logs older than {days} days. "
                f"Cutoff: {cutoff.isoformat()}"
            )
            deleted_count, _ = logs.delete()
            logger.info(f"Successfully deleted {deleted_count} old audit logs")
            return {"deleted_count": deleted_count, "days": days}
        else:
            logger.info("No old audit logs to clean up")
            return {"deleted_count": 0, "days": days}
    except Exception as exc:
        logger.error(f"Failed to cleanup old audit logs: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def export_audit_logs_task(self, organization_id, start_date, end_date):
    """Export audit logs to file."""
    from apps.audit.models import AuditLog
    import json
    import csv
    import io
    from datetime import datetime

    try:
        start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date

        logs = AuditLog.objects.filter(
            organization_id=organization_id,
            created_at__gte=start,
            created_at__lte=end,
        ).order_by("created_at")

        # Generate CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "actor", "actor_type", "action", "target_type", "target_id",
            "ip_address", "created_at", "metadata"
        ])

        for log in logs:
            writer.writerow([
                log.id,
                log.actor_id or "",
                log.actor_type,
                log.action,
                log.target_type,
                log.target_id,
                log.ip_address or "",
                log.created_at.isoformat(),
                json.dumps(log.metadata) if log.metadata else "",
            ])

        csv_content = output.getvalue()
        output.close()

        result = {
            "organization_id": organization_id,
            "start_date": str(start),
            "end_date": str(end),
            "total_logs": logs.count(),
            "csv_size_bytes": len(csv_content),
        }

        logger.info(
            f"Audit logs exported for org {organization_id}: "
            f"{result['total_logs']} logs ({result['csv_size_bytes']} bytes)"
        )
        return result
    except Exception as exc:
        logger.error(f"Failed to export audit logs for org {organization_id}: {exc}")
        self.retry(exc=exc)
