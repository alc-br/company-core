import pytest
from apps.billing.services import BillingService


class TestBillingService:
    def test_create_subscription(self, db):
        from apps.organizations.services import OrganizationService
        from apps.billing.models import Plan
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="owner@example.com", password="pass123")
        org = OrganizationService.create_organization(name="Test", owner=user)
        plan = Plan.objects.create(name="Pro", price_cents=4900)
        
        sub = BillingService.create_subscription(org, plan, stripe_customer_id="cus_123")
        assert sub.organization == org
        assert sub.plan == plan
