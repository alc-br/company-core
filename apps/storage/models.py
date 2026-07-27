from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import StorageBackendType


class StorageBackendConfig(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    backend_type = models.IntegerField(choices=StorageBackendType.choices, verbose_name=_("Tipo"))
    config_encrypted = models.BinaryField(null=True, blank=True, verbose_name=_("Configuração"))
    is_default = models.BooleanField(default=False, verbose_name=_("Padrão"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="storage_configs",
        verbose_name=_("Organização"),
    )

    class Meta:
        verbose_name = _("Configuração de Storage")
        verbose_name_plural = _("Configurações de Storage")

    def __str__(self):
        return self.name


class StoredObject(TimestampMixin):
    key = models.CharField(max_length=1000, verbose_name=_("Chave"))
    bucket = models.CharField(max_length=255, verbose_name=_("Bucket"))
    size = models.PositiveBigIntegerField(default=0, verbose_name=_("Tamanho"))
    content_type = models.CharField(max_length=255, verbose_name=_("Content Type"))
    checksum = models.CharField(max_length=255, blank=True, verbose_name=_("Checksum"))
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Uploaded by"),
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="stored_objects",
        verbose_name=_("Organização"),
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))

    class Meta:
        verbose_name = _("Objeto Armazenado")
        verbose_name_plural = _("Objetos Armazenados")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "key"])]

    def __str__(self):
        return f"{self.key} ({self.content_type})"
