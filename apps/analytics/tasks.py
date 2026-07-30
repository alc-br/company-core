import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def compute_daily_metrics_task(self):
    """Compute daily metrics for all organizations."""
    from apps.analytics.models import AnalyticsAggregation, AnalyticsEvent
    from apps.organizations.models import Organization

    try:
        yesterday = (timezone.now() - timedelta(days=1)).date()
        organizations = Organization.objects.filter(status=1)  # ACTIVE
        total_computed = 0

        for org in organizations:
            events = AnalyticsEvent.objects.filter(
                organization=org,
                timestamp__date=yesterday,
            )

            # Aggregate by module and event_type
            module_metrics = events.values("module").annotate(
                event_count=Count("id"),
            )

            for metric in module_metrics:
                module = metric["module"]
                module_events = events.filter(module=module)

                event_types = module_events.values("event_type").annotate(
                    type_count=Count("id"),
                )

                for et in event_types:
                    AnalyticsAggregation.objects.update_or_create(
                        organization=org,
                        period=yesterday,
                        module=module,
                        metric=et["event_type"],
                        defaults={"value": et["type_count"]},
                    )

                total_computed += len(event_types)

        logger.info(f"Daily metrics computed for {organizations.count()} organizations ({total_computed} metrics)")
        return {"date": str(yesterday), "organizations": organizations.count(), "metrics": total_computed}
    except Exception as exc:
        logger.error(f"Failed to compute daily metrics: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_organization_report_task(self, organization_id):
    """Generate a report for an organization."""
    from apps.analytics.models import AnalyticsAggregation, AnalyticsEvent
    from apps.organizations.models import Organization
    from datetime import timedelta

    try:
        org = Organization.objects.get(id=organization_id)
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)

        # Events summary for last 7 days
        recent_events = AnalyticsEvent.objects.filter(
            organization=org,
            timestamp__gte=last_7_days,
        )
        recent_summary = recent_events.values("module").annotate(
            event_count=Count("id"),
        ).order_by("-event_count")

        # Events summary for last 30 days
        monthly_events = AnalyticsEvent.objects.filter(
            organization=org,
            timestamp__gte=last_30_days,
        )
        monthly_summary = monthly_events.values("module").annotate(
            event_count=Count("id"),
        ).order_by("-event_count")

        # Top event types
        top_events = recent_events.values("event_type").annotate(
            event_count=Count("id"),
        ).order_by("-event_count")[:10]

        report = {
            "organization_id": organization_id,
            "organization_name": org.name,
            "generated_at": now.isoformat(),
            "period_7d": {
                "total_events": recent_events.count(),
                "by_module": list(recent_summary),
            },
            "period_30d": {
                "total_events": monthly_events.count(),
                "by_module": list(monthly_summary),
            },
            "top_event_types": list(top_events),
        }

        logger.info(f"Report generated for organization {organization_id}")
        return report
    except Organization.DoesNotExist:
        logger.error(f"Organization {organization_id} not found for report generation")
        return None
    except Exception as exc:
        logger.error(f"Failed to generate report for organization {organization_id}: {exc}")
        self.retry(exc=exc)
