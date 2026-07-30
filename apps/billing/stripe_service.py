import logging
import stripe
from django.conf import settings

logger = logging.getLogger(__name__)


class StripeService:
    """Service for interacting with the Stripe API."""

    @staticmethod
    def _get_api_key():
        """Get the Stripe API key from settings or environment."""
        key = getattr(settings, "STRIPE_SECRET_KEY", None)
        if not key:
            import os
            key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not key:
            logger.warning("Stripe secret key not configured")
        return key

    @staticmethod
    def create_checkout_session(organization, plan, success_url, cancel_url):
        """Create a Stripe Checkout session for a subscription.

        Args:
            organization: Organization model instance
            plan: Plan model instance with stripe_price_id
            success_url: URL to redirect to on success
            cancel_url: URL to redirect to on cancel

        Returns:
            stripe.checkout.Session object or None
        """
        api_key = StripeService._get_api_key()
        if not api_key:
            logger.error("Cannot create checkout session: Stripe key not configured")
            return None

        try:
            stripe.api_key = api_key

            customer_id = ""
            # Check if organization already has a Stripe customer
            from apps.billing.models import Subscription
            existing_sub = Subscription.objects.filter(
                organization=organization,
                stripe_customer_id__gt="",
            ).first()
            if existing_sub:
                customer_id = existing_sub.stripe_customer_id

            session_params = {
                "mode": "subscription",
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": plan.stripe_price_id,
                        "quantity": 1,
                    },
                ],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    "organization_id": str(organization.id),
                    "plan_id": str(plan.id),
                },
            }

            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_email"] = organization.owner.email if organization.owner else ""

            session = stripe.checkout.Session.create(**session_params)
            logger.info(
                f"Stripe checkout session created: {session.id} for "
                f"org {organization.id}, plan {plan.id}"
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout session creation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating checkout session: {e}")
            return None

    @staticmethod
    def create_customer(email, name=None, metadata=None):
        """Create a Stripe customer.

        Args:
            email: Customer email address
            name: Optional customer name
            metadata: Optional dict of metadata

        Returns:
            stripe.Customer object or None
        """
        api_key = StripeService._get_api_key()
        if not api_key:
            logger.error("Cannot create customer: Stripe key not configured")
            return None

        try:
            stripe.api_key = api_key
            customer_params = {
                "email": email,
                "metadata": metadata or {},
            }
            if name:
                customer_params["name"] = name

            customer = stripe.Customer.create(**customer_params)
            logger.info(f"Stripe customer created: {customer.id} ({email})")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Stripe customer: {e}")
            return None

    @staticmethod
    def create_subscription(customer_id, price_id, trial_days=None):
        """Create a Stripe subscription.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Optional trial period days

        Returns:
            stripe.Subscription object or None
        """
        api_key = StripeService._get_api_key()
        if not api_key:
            logger.error("Cannot create subscription: Stripe key not configured")
            return None

        try:
            stripe.api_key = api_key
            sub_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
            }
            if trial_days:
                sub_params["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**sub_params)
            logger.info(f"Stripe subscription created: {subscription.id} for customer {customer_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription creation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Stripe subscription: {e}")
            return None

    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancel a Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            stripe.Subscription object or None
        """
        api_key = StripeService._get_api_key()
        if not api_key:
            logger.error("Cannot cancel subscription: Stripe key not configured")
            return None

        try:
            stripe.api_key = api_key
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
            logger.info(f"Stripe subscription canceled at period end: {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription cancellation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error canceling Stripe subscription: {e}")
            return None

    @staticmethod
    def construct_webhook_event(payload, sig_header):
        """Verify and construct a Stripe webhook event.

        Args:
            payload: Raw request body as bytes
            sig_header: Stripe-Signature header value

        Returns:
            stripe.Event object or None
        """
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        if not webhook_secret:
            try:
                import os
                webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
            except Exception:
                pass

        if not webhook_secret:
            logger.error("Cannot verify webhook: STRIPE_WEBHOOK_SECRET not configured")
            return None

        try:
            return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error constructing Stripe webhook event: {e}")
            return None

    @staticmethod
    def handle_webhook_event(event):
        """Route a Stripe webhook event to the appropriate handler.

        Handles:
        - checkout.session.completed
        - customer.subscription.created
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_failed
        - invoice.payment_succeeded
        """
        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        logger.info(f"Processing Stripe webhook event: {event_type}")

        handlers = {
            "checkout.session.completed": StripeService._handle_checkout_completed,
            "customer.subscription.created": StripeService._handle_subscription_created,
            "customer.subscription.updated": StripeService._handle_subscription_updated,
            "customer.subscription.deleted": StripeService._handle_subscription_deleted,
            "invoice.payment_failed": StripeService._handle_invoice_payment_failed,
            "invoice.payment_succeeded": StripeService._handle_invoice_payment_succeeded,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                handler(data)
                logger.info(f"Stripe webhook event handled successfully: {event_type}")
                return True
            except Exception as e:
                logger.error(f"Error handling Stripe webhook event {event_type}: {e}")
                return False
        else:
            logger.info(f"No handler for Stripe webhook event type: {event_type}")
            return True  # Unhandled events are not errors

    @staticmethod
    def _handle_checkout_completed(session_data):
        """Handle checkout.session.completed event."""
        from apps.billing.models import Subscription, Plan, Organization
        from apps.common.constants import SubscriptionStatus

        metadata = session_data.get("metadata", {})
        org_id = metadata.get("organization_id")
        plan_id = metadata.get("plan_id")

        if not org_id or not plan_id:
            logger.warning("Checkout completed but missing metadata (org_id, plan_id)")
            return

        try:
            organization = Organization.objects.get(id=org_id)
            plan = Plan.objects.get(id=plan_id)

            # Get or create subscription
            stripe_sub_id = session_data.get("subscription", "")
            stripe_customer_id = session_data.get("customer", "")

            subscription, created = Subscription.objects.update_or_create(
                organization=organization,
                plan=plan,
                defaults={
                    "stripe_subscription_id": stripe_sub_id,
                    "stripe_customer_id": stripe_customer_id,
                    "status": SubscriptionStatus.ACTIVE,
                },
            )

            if created:
                logger.info(f"Subscription created from checkout: {subscription.id}")
            else:
                logger.info(f"Subscription updated from checkout: {subscription.id}")

        except Organization.DoesNotExist:
            logger.error(f"Organization {org_id} not found during checkout completion")
        except Plan.DoesNotExist:
            logger.error(f"Plan {plan_id} not found during checkout completion")

    @staticmethod
    def _handle_subscription_created(sub_data):
        """Handle customer.subscription.created event."""
        from apps.billing.models import Subscription
        from apps.common.constants import SubscriptionStatus

        stripe_sub_id = sub_data.get("id", "")
        stripe_customer_id = sub_data.get("customer", "")
        metadata = sub_data.get("metadata", {})
        org_id = metadata.get("organization_id")

        if not org_id:
            logger.warning(f"Subscription created without org_id in metadata: {stripe_sub_id}")
            return

        try:
            sub = Subscription.objects.filter(
                organization_id=org_id,
            ).order_by("-created_at").first()

            if sub:
                sub.stripe_subscription_id = stripe_sub_id
                sub.stripe_customer_id = stripe_customer_id
                sub.status = SubscriptionStatus.ACTIVE
                sub.current_period_start = sub_data.get("current_period_start")
                sub.current_period_end = sub_data.get("current_period_end")
                if sub_data.get("trial_end"):
                    sub.trial_end = sub_data.get("trial_end")
                sub.save()
                logger.info(f"Subscription {sub.id} updated with Stripe data")
        except Exception as e:
            logger.error(f"Error handling subscription created: {e}")

    @staticmethod
    def _handle_subscription_updated(sub_data):
        """Handle customer.subscription.updated event."""
        from apps.billing.models import Subscription
        from apps.common.constants import SubscriptionStatus

        stripe_sub_id = sub_data.get("id", "")
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "trialing": SubscriptionStatus.TRIALING,
            "paused": SubscriptionStatus.PAUSED,
            "unpaid": SubscriptionStatus.UNPAID,
        }

        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            stripe_status = sub_data.get("status", "")
            new_status = status_map.get(stripe_status, sub.status)

            sub.status = new_status
            if sub_data.get("current_period_start"):
                sub.current_period_start = sub_data.get("current_period_start")
            if sub_data.get("current_period_end"):
                sub.current_period_end = sub_data.get("current_period_end")
            if sub_data.get("cancel_at_period_end") is not None:
                sub.cancel_at_period_end = sub_data.get("cancel_at_period_end")
            sub.save()
            logger.info(f"Subscription {sub.id} updated via Stripe webhook to {new_status}")
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found for Stripe ID: {stripe_sub_id}")

    @staticmethod
    def _handle_subscription_deleted(sub_data):
        """Handle customer.subscription.deleted event."""
        from apps.billing.models import Subscription
        from apps.common.constants import SubscriptionStatus

        stripe_sub_id = sub_data.get("id", "")

        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            sub.status = SubscriptionStatus.CANCELED
            sub.cancel_at_period_end = False
            sub.save()
            logger.info(f"Subscription {sub.id} canceled via Stripe webhook")
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found for Stripe ID (deleted): {stripe_sub_id}")

    @staticmethod
    def _handle_invoice_payment_failed(invoice_data):
        """Handle invoice.payment_failed event."""
        from apps.billing.models import Subscription, Invoice
        from apps.common.constants import SubscriptionStatus

        stripe_invoice_id = invoice_data.get("id", "")
        stripe_sub_id = invoice_data.get("subscription", "")
        amount = invoice_data.get("amount_due", 0)

        # Update the invoice status
        try:
            invoice = Invoice.objects.filter(stripe_invoice_id=stripe_invoice_id).first()
            if invoice:
                invoice.status = "failed"
                invoice.save()
        except Exception as e:
            logger.error(f"Error updating invoice {stripe_invoice_id}: {e}")

        # Mark the subscription as past due
        if stripe_sub_id:
            try:
                sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
                sub.status = SubscriptionStatus.PAST_DUE
                sub.save()
                logger.warning(f"Subscription {sub.id} marked as past due due to failed payment")
            except Subscription.DoesNotExist:
                logger.warning(f"Subscription not found for Stripe ID: {stripe_sub_id}")

    @staticmethod
    def _handle_invoice_payment_succeeded(invoice_data):
        """Handle invoice.payment_succeeded event."""
        from apps.billing.models import Subscription, Invoice
        from apps.common.constants import SubscriptionStatus
        from django.utils import timezone

        stripe_invoice_id = invoice_data.get("id", "")
        stripe_sub_id = invoice_data.get("subscription", "")
        amount_paid = invoice_data.get("amount_paid", 0)

        # Update the invoice
        try:
            invoice = Invoice.objects.filter(stripe_invoice_id=stripe_invoice_id).first()
            if invoice:
                invoice.status = "paid"
                invoice.amount_cents = amount_paid
                invoice.paid_at = timezone.now()
                invoice.save()
            elif stripe_sub_id:
                # Create invoice record if it doesn't exist
                sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
                if sub:
                    Invoice.objects.create(
                        organization=sub.organization,
                        subscription=sub,
                        stripe_invoice_id=stripe_invoice_id,
                        amount_cents=amount_paid,
                        status="paid",
                        paid_at=timezone.now(),
                    )
        except Exception as e:
            logger.error(f"Error processing invoice payment succeeded: {e}")

        # Reactivate subscription if it was past due
        if stripe_sub_id:
            try:
                sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
                if sub.status == SubscriptionStatus.PAST_DUE:
                    sub.status = SubscriptionStatus.ACTIVE
                    sub.save()
                    logger.info(f"Subscription {sub.id} reactivated after successful payment")
            except Subscription.DoesNotExist:
                pass
