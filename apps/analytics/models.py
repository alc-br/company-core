from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class AnalyticsEvent(TimestampMixin):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="analytics_events",
        verbose_name=_("Tenant"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Usuário"),
    )
    event_type = models.CharField(max_length=255, verbose_name=_("Tipo"))
    module = models.CharField(max_length=100, verbose_name=_("Módulo"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    class Meta:
        verbose_name = _("Evento de Analytics")
        verbose_name_plural = _("Eventos de Analytics")
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["organization", "event_type", "timestamp"])]

    def __str__(self):
        return f"{self.event_type} ({self.module})"


class AnalyticsAggregation(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="analytics_aggregations",
        verbose_name=_("Tenant"),
    )
    period = models.DateField(verbose_name=_("Período"))
    module = models.CharField(max_length=100, verbose_name=_("Módulo"))
    metric = models.CharField(max_length=255, verbose_name=_("Métrica"))
    value = models.DecimalField(max_digits=20, decimal_places=6, default=0, verbose_name=_("Valor"))

    class Meta:
        verbose_name = _("Agregação de Analytics")
        verbose_name_plural = _("Agregações de Analytics")
        unique_together = ["organization", "period", "module", "metric"]

    def __str__(self):
        return f"{self.metric}: {self.value}"
