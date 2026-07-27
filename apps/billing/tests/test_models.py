import pytest
from apps.billing.models import Plan, Subscription


class TestPlanModel:
    def test_plan_str(self):
        plan = Plan(name="Pro Plan")
        assert str(plan) == "Pro Plan"


class TestSubscriptionModel:
    def test_subscription_fields(self):
        sub = Subscription()
        assert hasattr(sub, "organization")
        assert hasattr(sub, "plan")
        assert hasattr(sub, "status")
