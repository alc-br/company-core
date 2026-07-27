from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class Integration(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    integration_type = models.CharField(max_length=100, verbose_name=_("Tipo"))
    credentials_encrypted = models.BinaryField(null=True, blank=True, verbose_name=_("Credenciais"))
    status = models.CharField(max_length=50, default="active", verbose_name=_("Status"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="integrations",
        verbose_name=_("Organização"),
    )
    last_health_check = models.DateTimeField(null=True, blank=True, verbose_name=_("Último Health Check"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))

    class Meta:
        verbose_name = _("Integração")
        verbose_name_plural = _("Integrações")
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class IntegrationLog(TimestampMixin):
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name=_("Integração"),
    )
    action = models.CharField(max_length=255, verbose_name=_("Ação"))
    request_data = models.JSONField(default=dict, verbose_name=_("Request"))
    response_data = models.JSONField(default=dict, verbose_name=_("Response"))
    status = models.CharField(max_length=50, verbose_name=_("Status"))
    duration_ms = models.PositiveIntegerField(default=0, verbose_name=_("Duração"))
    error_message = models.TextField(blank=True, verbose_name=_("Erro"))

    class Meta:
        verbose_name = _("Log de Integração")
        verbose_name_plural = _("Logs de Integração")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.status}"
