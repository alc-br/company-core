from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class WebhookEndpoint(TimestampMixin):
    url = models.URLField(max_length=2000, verbose_name=_("URL"))
    secret_encrypted = models.BinaryField(null=True, blank=True, verbose_name=_("Secret"))
    events = models.JSONField(default=list, blank=True, verbose_name=_("Eventos"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
        verbose_name=_("Organização"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Webhook Endpoint")
        verbose_name_plural = _("Webhook Endpoints")

    def __str__(self):
        return self.url


class WebhookDelivery(TimestampMixin):
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name="deliveries",
        verbose_name=_("Endpoint"),
    )
    event_type = models.CharField(max_length=255, verbose_name=_("Tipo de Evento"))
    payload = models.JSONField(default=dict, verbose_name=_("Payload"))
    status = models.CharField(max_length=50, default="pending", verbose_name=_("Status"))
    attempts = models.PositiveIntegerField(default=0, verbose_name=_("Tentativas"))
    response_code = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Código de Resposta"))
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Última Tentativa"))

    class Meta:
        verbose_name = _("Entrega de Webhook")
        verbose_name_plural = _("Entregas de Webhooks")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} - {self.status}"
