from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class AuditLog(TimestampMixin):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("Ator"),
    )
    actor_type = models.CharField(max_length=50, default="user", verbose_name=_("Tipo do Ator"))
    action = models.CharField(max_length=255, verbose_name=_("Ação"))
    target_type = models.CharField(max_length=255, verbose_name=_("Tipo do Alvo"))
    target_id = models.CharField(max_length=255, blank=True, verbose_name=_("ID do Alvo"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("Organização"),
    )

    class Meta:
        verbose_name = _("Log de Auditoria")
        verbose_name_plural = _("Logs de Auditoria")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor", "-created_at"]),
            models.Index(fields=["action"]),
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["organization", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.target_type} by {self.actor}"
