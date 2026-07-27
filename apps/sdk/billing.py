class BillingSDK:
    @staticmethod
    def get_active_plan(organization_id):
        from apps.billing.selectors import get_active_plans
        from apps.billing.services import BillingService
        return BillingService.get_active_subscription(organization_id)

    @staticmethod
    def check_subscription_active(organization_id):
        sub = BillingSDK.get_active_plan(organization_id)
        return sub is not None
