from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin


class ExportJob(TenantMixin, TimestampMixin):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pendente")),
        (STATUS_COMPLETED, _("Concluida")),
        (STATUS_FAILED, _("Falhou")),
    ]

    type = models.CharField(max_length=50, verbose_name=_("Tipo"))
    format = models.CharField(max_length=10, default="csv", verbose_name=_("Formato"))
    filters = models.JSONField(default=dict, blank=True, verbose_name=_("Filtros"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name=_("Status"))
    stored_object = models.ForeignKey(
        "storage.StoredObject", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", verbose_name=_("Arquivo"),
    )
    error_message = models.TextField(blank=True, verbose_name=_("Erro"))
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="export_jobs", verbose_name=_("Solicitado por"),
    )

    class Meta:
        verbose_name = _("Exportacao")
        verbose_name_plural = _("Exportacoes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} ({self.status})"
