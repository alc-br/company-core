import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_invoice_task(self, subscription_id):
    """Generate and process an invoice for a subscription."""
    from apps.billing.models import Subscription, Invoice
    from apps.common.constants import SubscriptionStatus

    try:
        subscription = Subscription.objects.select_related("organization", "plan").get(id=subscription_id)
    except Subscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found for invoice processing")
        return

    try:
        if subscription.status == SubscriptionStatus.ACTIVE:
            invoice = Invoice.objects.create(
                organization=subscription.organization,
                subscription=subscription,
                amount_cents=subscription.plan.price_cents,
                status="pending",
                due_date=timezone.now(),
            )
            logger.info(f"Invoice {invoice.id} created for subscription {subscription_id}")
            return {"invoice_id": invoice.id, "amount": invoice.amount_cents}
        else:
            logger.warning(f"Subscription {subscription_id} is not active, skipping invoice")
            return None
    except Exception as exc:
        logger.error(f"Failed to process invoice for subscription {subscription_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def check_overdue_subscriptions_task(self):
    """Check and mark overdue subscriptions."""
    from apps.billing.models import Subscription
    from apps.common.constants import SubscriptionStatus

    try:
        now = timezone.now()
        overdue_count = 0

        active_subs = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            current_period_end__lt=now,
        )
        for sub in active_subs:
            sub.status = SubscriptionStatus.PAST_DUE
            sub.save()
            overdue_count += 1
            logger.info(f"Subscription {sub.id} marked as overdue")

        logger.info(f"Check complete: {overdue_count} overdue subscriptions found")
        return {"overdue_count": overdue_count}
    except Exception as exc:
        logger.error(f"Failed to check overdue subscriptions: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_stripe_subscription_task(self, subscription_id):
    """Sync subscription status with Stripe."""
    from apps.billing.models import Subscription
    from apps.common.constants import SubscriptionStatus

    try:
        subscription = Subscription.objects.get(id=subscription_id)

        if not subscription.stripe_subscription_id:
            logger.warning(f"Subscription {subscription_id} has no Stripe subscription ID")
            return None

        stripe_secret_key = None
        try:
            from django.conf import settings
            stripe_secret_key = getattr(settings, "STRIPE_SECRET_KEY", None)
        except Exception:
            pass

        if not stripe_secret_key:
            logger.warning("Stripe secret key not configured, skipping sync")
            return None

        try:
            import stripe as stripe_lib
            stripe_lib.api_key = stripe_secret_key
            stripe_sub = stripe_lib.Subscription.retrieve(subscription.stripe_subscription_id)

            status_map = {
                "active": SubscriptionStatus.ACTIVE,
                "past_due": SubscriptionStatus.PAST_DUE,
                "canceled": SubscriptionStatus.CANCELED,
                "trialing": SubscriptionStatus.TRIALING,
                "paused": SubscriptionStatus.PAUSED,
                "unpaid": SubscriptionStatus.UNPAID,
            }
            new_status = status_map.get(stripe_sub.status, subscription.status)

            if new_status != subscription.status:
                subscription.status = new_status
                subscription.save()
                logger.info(f"Subscription {subscription_id} synced to status {new_status}")

            if stripe_sub.current_period_start:
                subscription.current_period_start = stripe_sub.current_period_start
            if stripe_sub.current_period_end:
                subscription.current_period_end = stripe_sub.current_period_end
            if stripe_sub.cancel_at_period_end is not None:
                subscription.cancel_at_period_end = stripe_sub.cancel_at_period_end
            subscription.save()

            logger.info(f"Subscription {subscription_id} synced with Stripe successfully")
            return {"subscription_id": subscription_id, "status": subscription.get_status_display()}
        except ImportError:
            logger.warning("Stripe library not installed, skipping sync")
            return None
    except Subscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found for Stripe sync")
        return None
    except Exception as exc:
        logger.error(f"Failed to sync subscription {subscription_id} with Stripe: {exc}")
        self.retry(exc=exc)
