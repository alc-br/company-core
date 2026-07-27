from apps.billing.models import Plan, Subscription
from apps.common.constants import SubscriptionStatus


def get_active_plans():
    return Plan.objects.filter(is_active=True).order_by("display_order", "price_cents")


def get_subscription_by_id(subscription_id):
    return Subscription.objects.select_related("plan", "organization").get(id=subscription_id)


def get_org_subscriptions(organization_id, *, status=None):
    qs = Subscription.objects.filter(organization_id=organization_id).select_related("plan")
    if status is not None:
        qs = qs.filter(status=status)
    return qs
