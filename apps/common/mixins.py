from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Mixin that adds created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True


class TenantMixin(models.Model):
    """Mixin that adds organization/tenant scope to any model."""

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        verbose_name="Organização",
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin that adds soft delete functionality."""

    is_deleted = models.BooleanField(default=False, verbose_name="Deletado")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deletado em")

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])
