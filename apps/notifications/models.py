from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import NotificationChannelType


class NotificationChannel(TimestampMixin):
    type = models.IntegerField(choices=NotificationChannelType.choices, verbose_name=_("Tipo"))
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    config_encrypted = models.BinaryField(null=True, blank=True, verbose_name=_("Configuração"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="notification_channels",
        verbose_name=_("Organização"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Canal de Notificação")
        verbose_name_plural = _("Canais de Notificação")

    def __str__(self):
        return self.name


class NotificationTemplate(TimestampMixin):
    code = models.CharField(max_length=255, unique=True, verbose_name=_("Código"))
    subject = models.CharField(max_length=500, verbose_name=_("Assunto"))
    body_html = models.TextField(blank=True, verbose_name=_("HTML"))
    body_text = models.TextField(blank=True, verbose_name=_("Texto"))
    channel = models.CharField(max_length=100, default="email", verbose_name=_("Canal"))

    class Meta:
        verbose_name = _("Template de Notificação")
        verbose_name_plural = _("Templates de Notificação")

    def __str__(self):
        return self.code


class NotificationLog(TimestampMixin):
    channel = models.ForeignKey(
        NotificationChannel,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Canal"),
    )
    recipient = models.EmailField(verbose_name=_("Destinatário"))
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Template"),
    )
    status = models.CharField(max_length=50, default="pending", verbose_name=_("Status"))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Enviado em"))
    error_message = models.TextField(blank=True, verbose_name=_("Erro"))

    class Meta:
        verbose_name = _("Log de Notificação")
        verbose_name_plural = _("Logs de Notificação")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.status}"
