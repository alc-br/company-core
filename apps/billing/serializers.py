from rest_framework import serializers
from apps.billing.models import Plan, Subscription, Invoice
from apps.common.constants import BillingCycle, SubscriptionStatus


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for Plan model."""

    billing_cycle_display = serializers.CharField(
        source="get_billing_cycle_display", read_only=True
    )

    class Meta:
        model = Plan
        fields = (
            "id", "name", "stripe_price_id", "description", "features",
            "limits", "price_cents", "billing_cycle", "billing_cycle_display",
            "is_active", "display_order", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for plan list views."""

    billing_cycle_display = serializers.CharField(
        source="get_billing_cycle_display", read_only=True
    )

    class Meta:
        model = Plan
        fields = (
            "id", "name", "price_cents", "billing_cycle",
            "billing_cycle_display", "is_active", "display_order",
        )
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    plan_name = serializers.CharField(
        source="plan.name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            "id", "organization", "organization_name", "plan", "plan_name",
            "stripe_subscription_id", "stripe_customer_id",
            "status", "status_display",
            "current_period_start", "current_period_end",
            "cancel_at_period_end", "trial_end",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for subscription list views."""

    plan_name = serializers.CharField(
        source="plan.name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            "id", "plan", "plan_name", "status", "status_display",
            "current_period_start", "current_period_end",
            "cancel_at_period_end", "created_at",
        )
        read_only_fields = fields


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    subscription_plan = serializers.CharField(
        source="subscription.plan.name", read_only=True
    )

    class Meta:
        model = Invoice
        fields = (
            "id", "organization", "organization_name", "subscription",
            "subscription_plan", "stripe_invoice_id", "amount_cents",
            "status", "paid_at", "due_date",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
