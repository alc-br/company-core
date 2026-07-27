class QuotaSDK:
    @staticmethod
    def check(organization_id, quota_code, increment=1):
        from apps.quotas.services import QuotaService
        return QuotaService.check_quota(organization_id, quota_code, increment)

    @staticmethod
    def get_status(organization_id, quota_code):
        from apps.quotas.services import QuotaService
        return QuotaService.get_quota_status(organization_id, quota_code)
