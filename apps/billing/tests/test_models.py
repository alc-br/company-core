import pytest
from apps.billing.models import Plan, Subscription


class TestPlanModel:
    def test_plan_str(self):
        plan = Plan(name="Pro Plan")
        assert str(plan) == "Pro Plan"


class TestSubscriptionModel:
    def test_subscription_fields(self):
        from django.db.models.fields.related import ForeignKey
        assert any(f.name == "organization" for f in Subscription._meta.get_fields())
        assert any(f.name == "plan" for f in Subscription._meta.get_fields())
        assert any(f.name == "status" for f in Subscription._meta.get_fields())
