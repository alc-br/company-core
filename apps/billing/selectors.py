from apps.billing.models import Plan, Subscription, Invoice
from apps.common.constants import SubscriptionStatus
from typing import Optional
from django.db.models import QuerySet


def get_active_plans():
    return Plan.objects.filter(is_active=True).order_by("display_order", "price_cents")


def get_subscription_by_id(subscription_id):
    return Subscription.objects.select_related("plan", "organization").get(id=subscription_id)


def get_org_subscriptions(organization_id, *, status=None):
    qs = Subscription.objects.filter(organization_id=organization_id).select_related("plan")
    if status is not None:
        qs = qs.filter(status=status)
    return qs


def get_plan_queryset(
    *,
    is_active: Optional[bool] = None,
    billing_cycle: Optional[int] = None,
) -> QuerySet[Plan]:
    """Get plans queryset for API views."""
    queryset = Plan.objects.all()

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if billing_cycle is not None:
        queryset = queryset.filter(billing_cycle=billing_cycle)

    return queryset


def get_subscription_queryset(
    *,
    organization_id: Optional[int] = None,
    status: Optional[int] = None,
) -> QuerySet[Subscription]:
    """Get subscriptions queryset for API views."""
    queryset = Subscription.objects.select_related("plan", "organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    return queryset


def get_invoice_queryset(
    *,
    organization_id: Optional[int] = None,
    subscription_id: Optional[int] = None,
    status: Optional[str] = None,
) -> QuerySet[Invoice]:
    """Get invoices queryset for API views."""
    queryset = Invoice.objects.select_related("organization", "subscription", "subscription__plan")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if subscription_id is not None:
        queryset = queryset.filter(subscription_id=subscription_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    return queryset
