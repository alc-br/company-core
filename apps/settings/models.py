from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class TenantSetting(TimestampMixin):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name=_("Organização"),
    )
    key = models.CharField(max_length=255, verbose_name=_("Chave"))
    value = models.TextField(verbose_name=_("Valor"))
    environment = models.CharField(max_length=50, default="production", verbose_name=_("Ambiente"))

    class Meta:
        verbose_name = _("Configuração do Tenant")
        verbose_name_plural = _("Configurações do Tenant")
        unique_together = ["organization", "key", "environment"]

    def __str__(self):
        return f"{self.organization.name}: {self.key}"


class GlobalSetting(models.Model):
    key = models.CharField(max_length=255, unique=True, verbose_name=_("Chave"))
    value = models.TextField(verbose_name=_("Valor"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))

    class Meta:
        verbose_name = _("Configuração Global")
        verbose_name_plural = _("Configurações Globais")

    def __str__(self):
        return f"{self.key}"
