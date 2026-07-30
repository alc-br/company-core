import logging
from django.db import transaction, models as db_models
from django.utils import timezone
from apps.quotas.models import QuotaDefinition, QuotaAllocation
from apps.common.exceptions import QuotaExceededError, NotFoundException, ValidationError

logger = logging.getLogger(__name__)


class QuotaService:
    """Service layer for quota operations."""

    @staticmethod
    def check_quota(organization_id, quota_code, increment=1):
        """Check if quota allows the increment."""
        allocation = QuotaAllocation.objects.filter(
            organization_id=organization_id, definition__code=quota_code
        ).order_by("-period_start").first()

        if not allocation:
            return True  # No allocation = unlimited

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
        """Increment usage counter for a quota."""
        allocation = QuotaAllocation.objects.filter(
            organization_id=organization_id, definition__code=quota_code
        ).order_by("-period_start").first()

        if not allocation:
            return

        allocation.used = db_models.F("used") + amount
        allocation.save(update_fields=["used"])

    @staticmethod
    def get_quota_status(organization_id, quota_code):
        """Get detailed quota status."""
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
        """Initialize quotas for a new organization."""
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

    @staticmethod
    @transaction.atomic
    def update_quota_limit(organization_id, quota_code, new_limit):
        """Update the limit for a specific quota allocation."""
        allocation = QuotaAllocation.objects.filter(
            organization_id=organization_id, definition__code=quota_code
        ).order_by("-period_start").first()

        if not allocation:
            raise NotFoundException(
                message=f"No allocation found for quota '{quota_code}'",
                resource_type="quota_allocation",
            )

        allocation.limit = new_limit
        allocation.save()
        logger.info(f"Quota '{quota_code}' limit updated to {new_limit} for org {organization_id}")
        return allocation

    @staticmethod
    @transaction.atomic
    def reset_usage(organization_id, quota_code=None):
        """Reset usage counter for quota(s)."""
        qs = QuotaAllocation.objects.filter(organization_id=organization_id)
        if quota_code:
            qs = qs.filter(definition__code=quota_code)

        updated = qs.update(used=0)
        logger.info(f"Reset usage for {updated} quota allocations in org {organization_id}")
        return updated
