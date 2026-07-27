from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """Represents a granular permission in the system."""

    code = models.CharField(max_length=255, unique=True, verbose_name=_("Código"))
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    module = models.CharField(max_length=100, verbose_name=_("Módulo"))

    class Meta:
        verbose_name = _("Permissão")
        verbose_name_plural = _("Permissões")
        ordering = ["module", "code"]
        indexes = [models.Index(fields=["code"]), models.Index(fields=["module"])]

    def __str__(self):
        return f"{self.module}.{self.code}"


class Role(models.Model):
    """Represents a role with a set of permissions."""

    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("Organização"),
    )
    is_default = models.BooleanField(default=False, verbose_name=_("Papel padrão"))
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
        blank=True,
        verbose_name=_("Permissões"),
    )

    class Meta:
        verbose_name = _("Papel")
        verbose_name_plural = _("Papéis")
        ordering = ["name"]
        unique_together = ["name", "organization"]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class RolePermission(models.Model):
    """Through table for Role-Permission relationship."""

    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Papel"))
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name=_("Permissão"))

    class Meta:
        verbose_name = _("Permissão do Papel")
        verbose_name_plural = _("Permissões do Papel")
        unique_together = ["role", "permission"]

    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"
