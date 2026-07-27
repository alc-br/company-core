import logging
from django.db import transaction
from apps.billing.models import Plan, Subscription, Invoice
from apps.common.exceptions import NotFoundException, ServiceException

logger = logging.getLogger(__name__)


class BillingService:
    @staticmethod
    @transaction.atomic
    def create_subscription(organization, plan, stripe_customer_id="", stripe_subscription_id=""):
        subscription = Subscription.objects.create(
            organization=organization,
            plan=plan,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            status=1,  # ACTIVE
        )
        logger.info(f"Subscription created for org {organization.id}, plan {plan.id}")
        return subscription

    @staticmethod
    @transaction.atomic
    def cancel_subscription(subscription, at_period_end=True):
        subscription.status = 3  # CANCELED
        subscription.cancel_at_period_end = at_period_end
        subscription.save()
        logger.info(f"Subscription {subscription.id} canceled")
        return subscription

    @staticmethod
    @transaction.atomic
    def change_plan(subscription, new_plan):
        old_plan = subscription.plan
        subscription.plan = new_plan
        subscription.save()
        logger.info(f"Subscription {subscription.id} changed from {old_plan.name} to {new_plan.name}")
        return subscription

    @staticmethod
    def get_active_subscription(organization_id):
        return Subscription.objects.filter(
            organization_id=organization_id, status=1  # ACTIVE
        ).select_related("plan").first()
