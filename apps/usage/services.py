from django.db.models import Sum
from django.utils import timezone
from apps.usage.models import UsageRecord


class UsageService:
    @staticmethod
    def record_usage(organization, metric_type, value=1, unit="request", user=None, metadata=None):
        today = timezone.now().date()
        return UsageRecord.objects.create(
            organization=organization,
            user=user,
            metric_type=metric_type,
            value=value,
            unit=unit,
            period=today,
            metadata=metadata or {},
        )

    @staticmethod
    def get_usage_summary(organization, metric_type=None, period_start=None, period_end=None):
        queryset = UsageRecord.objects.filter(organization=organization)
        if metric_type is not None:
            queryset = queryset.filter(metric_type=metric_type)
        if period_start:
            queryset = queryset.filter(period__gte=period_start)
        if period_end:
            queryset = queryset.filter(period__lte=period_end)
        return queryset.values("metric_type").annotate(total=Sum("value")).order_by("metric_type")
