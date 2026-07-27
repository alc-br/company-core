from rest_framework.throttling import BaseThrottle


class TenantRateThrottle(BaseThrottle):
    def allow_request(self, request, view):
        return True  # To be implemented with plan-based limits
