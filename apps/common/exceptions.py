
class ServiceException(Exception):
    """Base exception for all service layer errors."""
    def __init__(self, message: str = "Service error occurred", code: str = "service_error"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(ServiceException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found", resource_type: str = None, resource_id=None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        code = f"{resource_type}_not_found" if resource_type else "not_found"
        super().__init__(message=message, code=code)


class PermissionDeniedError(ServiceException):
    """Raised when user lacks permission for an action."""
    def __init__(self, message: str = "Permission denied", permission: str = None):
        self.permission = permission
        super().__init__(message=message, code="permission_denied")


class QuotaExceededError(ServiceException):
    """Raised when a quota limit has been exceeded."""
    def __init__(self, message: str = "Quota exceeded", quota_code: str = None, current: int = 0, limit: int = 0):
        self.quota_code = quota_code
        self.current = current
        self.limit = limit
        super().__init__(message=message, code="quota_exceeded")


class ValidationError(ServiceException):
    """Raised when data validation fails."""
    def __init__(self, message: str = "Validation error", errors: dict = None):
        self.errors = errors or {}
        super().__init__(message=message, code="validation_error")


class IntegrationError(ServiceException):
    """Raised when an external integration fails."""
    def __init__(self, message: str = "Integration error", integration: str = None):
        self.integration = integration
        super().__init__(message=message, code="integration_error")


class AIProviderError(ServiceException):
    """Raised when an AI provider call fails."""
    def __init__(self, message: str = "AI provider error", provider: str = None):
        self.provider = provider
        super().__init__(message=message, code="ai_provider_error")
