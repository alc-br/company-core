from django.db import models
from django_stubs_ext.db.models import UserManager


class TenantManager(models.Manager):
    """Manager that automatically filters queries by the active tenant."""

    def get_queryset(self):
        queryset = super().get_queryset()
        from apps.organizations.utils import get_current_tenant
        tenant = get_current_tenant()
        if tenant:
            queryset = queryset.filter(organization=tenant)
        return queryset

    def for_tenant(self, organization):
        """Explicitly filter by a given organization."""
        return self.get_queryset().filter(organization=organization)


class ActiveManager(models.Manager):
    """Manager that filters for non-deleted records."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
