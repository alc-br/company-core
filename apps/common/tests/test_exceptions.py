import pytest
from apps.common.exceptions import (
    ServiceException,
    NotFoundException,
    PermissionDeniedError,
    QuotaExceededError,
    ValidationError,
    IntegrationError,
    AIProviderError,
)


class TestServiceException:
    def test_default_message(self):
        exc = ServiceException()
        assert exc.message == "Service error occurred"
        assert exc.code == "service_error"

    def test_custom_message(self):
        exc = ServiceException(message="Custom error", code="custom")
        assert exc.message == "Custom error"
        assert exc.code == "custom"


class TestNotFoundException:
    def test_default(self):
        exc = NotFoundException()
        assert exc.code == "not_found"

    def test_with_resource(self):
        exc = NotFoundException(resource_type="Organization", resource_id=1)
        assert exc.code == "Organization_not_found"


class TestPermissionDeniedError:
    def test_default(self):
        exc = PermissionDeniedError()
        assert exc.code == "permission_denied"

    def test_with_permission(self):
        exc = PermissionDeniedError(permission="admin_access")
        assert exc.permission == "admin_access"


class TestQuotaExceededError:
    def test_with_details(self):
        exc = QuotaExceededError(quota_code="ai_prompts", current=100, limit=50)
        assert exc.quota_code == "ai_prompts"
        assert exc.current == 100
        assert exc.limit == 50
