import threading

_tenant_context = threading.local()


def get_current_tenant():
    """Get the current tenant from thread-local storage."""
    return getattr(_tenant_context, "tenant", None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage."""
    _tenant_context.tenant = tenant


def clear_current_tenant():
    """Clear the current tenant from thread-local storage."""
    _tenant_context.tenant = None
