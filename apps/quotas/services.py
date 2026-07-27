import logging
from django.db import transaction, models
from django.utils import timezone
from apps.quotas.models import QuotaDefinition, QuotaAllocation
from apps.common.exceptions import QuotaExceededError, NotFoundException

logger = logging.getLogger(__name__)


class QuotaService:
    @staticmethod
    def check_quota(organization_id, quota_code, increment=1):
        allocation = QuotaAllocation.objects.filter(
            organization_id=organization_id, definition__code=quota_code
        ).order_by("-period_start").first()

        if not allocation:
            return True  # No allocation = unlimited (or use default)

        if allocation.used + increment > allocation.limit:
            raise QuotaExceededError(
                message=f"Quota '{quota_code}' exceeded",
                quota_code=quota_code,
                current=allocation.used,
                limit=allocation.limit,
            )
        return True

    @staticmethod
    @transaction.atomic
    def increment_usage(organization_id, quota_code, amount=1):
        allocation = QuotaAllocation.objects.filter(
            organization_id=organization_id, definition__code=quota_code
        ).order_by("-period_start").first()

        if not allocation:
            return

        allocation.used = models.F("used") + amount
        allocation.save(update_fields=["used"])

    @staticmethod
    def get_quota_status(organization_id, quota_code):
        allocation = QuotaAllocation.objects.filter(
            organization_id=organization_id, definition__code=quota_code
        ).select_related("definition").first()

        if not allocation:
            return None

        return {
            "code": allocation.definition.code,
            "name": allocation.definition.name,
            "unit": allocation.definition.unit,
            "limit": allocation.limit,
            "used": allocation.used,
            "remaining": allocation.remaining,
            "is_exceeded": allocation.is_exceeded,
        }

    @staticmethod
    @transaction.atomic
    def initialize_quotas(organization_id, plan_limits=None):
        from apps.quotas.models import QuotaDefinition
        definitions = QuotaDefinition.objects.all()
        plan_limits = plan_limits or {}

        for definition in definitions:
            limit = plan_limits.get(definition.code, definition.default_limit)
            QuotaAllocation.objects.update_or_create(
                organization_id=organization_id,
                definition=definition,
                period_start=timezone.now().date(),
                defaults={"limit": limit, "used": 0, "period_end": None},
            )
