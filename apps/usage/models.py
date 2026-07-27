from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import MetricType


class UsageRecord(TimestampMixin):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="usage_records",
        verbose_name=_("Organização"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usage_records",
        verbose_name=_("Usuário"),
    )
    metric_type = models.IntegerField(choices=MetricType.choices, verbose_name=_("Tipo de Métrica"))
    value = models.PositiveIntegerField(verbose_name=_("Valor"))
    unit = models.CharField(max_length=100, verbose_name=_("Unidade"))
    period = models.DateField(verbose_name=_("Período"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))

    class Meta:
        verbose_name = _("Registro de Uso")
        verbose_name_plural = _("Registros de Uso")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "metric_type", "period"])]

    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value} {self.unit}"
