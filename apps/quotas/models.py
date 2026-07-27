from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class QuotaDefinition(TimestampMixin):
    code = models.CharField(max_length=255, unique=True, verbose_name=_("Código"))
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    unit = models.CharField(max_length=100, verbose_name=_("Unidade"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    default_limit = models.PositiveIntegerField(default=0, verbose_name=_("Limite Padrão"))

    class Meta:
        verbose_name = _("Definição de Quota")
        verbose_name_plural = _("Definições de Quotas")
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.unit})"


class QuotaAllocation(TimestampMixin):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="quota_allocations", verbose_name=_("Organização"))
    definition = models.ForeignKey(QuotaDefinition, on_delete=models.CASCADE, related_name="allocations", verbose_name=_("Definição"))
    limit = models.PositiveIntegerField(verbose_name=_("Limite"))
    used = models.PositiveIntegerField(default=0, verbose_name=_("Usado"))
    period_start = models.DateField(verbose_name=_("Início do Período"))
    period_end = models.DateField(verbose_name=_("Fim do Período"))

    class Meta:
        verbose_name = _("Alocação de Quota")
        verbose_name_plural = _("Alocações de Quotas")
        unique_together = ["organization", "definition", "period_start"]
        indexes = [models.Index(fields=["organization", "definition"])]

    def __str__(self):
        return f"{self.organization.name} - {self.definition.code}: {self.used}/{self.limit}"

    @property
    def remaining(self):
        return max(0, self.limit - self.used)

    @property
    def is_exceeded(self):
        return self.used >= self.limit
