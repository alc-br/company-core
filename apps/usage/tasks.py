import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def record_usage_task(self, organization_id, metric_type, amount=1, metadata=None):
    """Record usage asynchronously."""
    from apps.usage.models import UsageRecord
    from apps.organizations.models import Organization

    try:
        organization = Organization.objects.get(id=organization_id)
        record = UsageRecord.objects.create(
            organization=organization,
            metric_type=metric_type,
            value=amount,
            unit="request",
            period=timezone.now().date(),
            metadata=metadata or {},
        )
        logger.info(
            f"Usage recorded: org={organization_id}, type={metric_type}, "
            f"amount={amount}, record_id={record.id}"
        )
        return {"record_id": record.id, "organization_id": organization_id, "metric_type": metric_type, "amount": amount}
    except Exception as exc:
        logger.error(f"Failed to record usage for org {organization_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def aggregate_usage_task(self, organization_id, period="daily"):
    """Aggregate usage data."""
    from apps.usage.models import UsageRecord
    from apps.organizations.models import Organization

    try:
        organization = Organization.objects.get(id=organization_id)

        if period == "daily":
            start = timezone.now().date() - timedelta(days=1)
            end = timezone.now().date()
        elif period == "weekly":
            start = timezone.now().date() - timedelta(weeks=1)
            end = timezone.now().date()
        elif period == "monthly":
            start = timezone.now().date() - timedelta(days=30)
            end = timezone.now().date()
        else:
            start = timezone.now().date() - timedelta(days=1)
            end = timezone.now().date()

        aggregation = UsageRecord.objects.filter(
            organization=organization,
            period__gte=start,
            period__lte=end,
        ).values("metric_type").annotate(
            total=Sum("value"),
            records=Sum("value"),  # same as total for simple metrics
        ).order_by("metric_type")

        result = {
            "organization_id": organization_id,
            "period": period,
            "start": str(start),
            "end": str(end),
            "metrics": list(aggregation),
        }

        logger.info(f"Usage aggregated for org {organization_id} ({period}): {len(aggregation)} metric types")
        return result
    except Exception as exc:
        logger.error(f"Failed to aggregate usage for org {organization_id}: {exc}")
        self.retry(exc=exc)
