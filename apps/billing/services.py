import logging
from django.db import transaction
from django.utils import timezone
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

    @staticmethod
    @transaction.atomic
    def create_plan(**kwargs):
        """Create a new billing plan."""
        plan = Plan.objects.create(**kwargs)
        logger.info(f"Plan '{plan.name}' created (id={plan.id})")
        return plan

    @staticmethod
    @transaction.atomic
    def update_plan(plan, **kwargs):
        """Update an existing billing plan."""
        for field, value in kwargs.items():
            if value is not None:
                setattr(plan, field, value)
        plan.save()
        logger.info(f"Plan '{plan.name}' updated (id={plan.id})")
        return plan

    @staticmethod
    @transaction.atomic
    def create_invoice(organization, subscription, amount_cents, stripe_invoice_id="", due_date=None):
        """Create a new invoice."""
        invoice = Invoice.objects.create(
            organization=organization,
            subscription=subscription,
            amount_cents=amount_cents,
            stripe_invoice_id=stripe_invoice_id,
            due_date=due_date,
            status="pending",
        )
        logger.info(f"Invoice {invoice.id} created for subscription {subscription.id}")
        return invoice

    @staticmethod
    @transaction.atomic
    def mark_invoice_paid(invoice):
        """Mark an invoice as paid."""
        invoice.status = "paid"
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=["status", "paid_at", "updated_at"])
        logger.info(f"Invoice {invoice.id} marked as paid")
        return invoice

    # ── Stripe Integration Methods ──────────────────────────────────────────

    @staticmethod
    def create_checkout(organization, plan, success_url, cancel_url):
        """Create a Stripe Checkout session for a subscription.

        Args:
            organization: Organization instance
            plan: Plan instance (must have stripe_price_id)
            success_url: URL to redirect to after successful payment
            cancel_url: URL to redirect to if payment is cancelled

        Returns:
            dict with session_id and url, or None on failure
        """
        from apps.billing.stripe_service import StripeService

        if not plan.stripe_price_id:
            logger.error(f"Plan {plan.id} has no Stripe price ID configured")
            return None

        session = StripeService.create_checkout_session(
            organization=organization,
            plan=plan,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        if session:
            return {
                "session_id": session.id,
                "url": session.url,
            }
        return None

    @staticmethod
    def handle_stripe_webhook(event):
        """Dispatch a Stripe webhook event to the appropriate handler.

        Args:
            event: Verified stripe.Event dict

        Returns:
            True if handled successfully, False otherwise
        """
        from apps.billing.stripe_service import StripeService

        return StripeService.handle_webhook_event(event)
