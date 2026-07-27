from django.db import models
from django.utils.translation import gettext_lazy as _


class SearchIndex(models.Model):
    content_type = models.CharField(max_length=255, verbose_name=_("Content Type"))
    object_id = models.CharField(max_length=255, verbose_name=_("Object ID"))
    content = models.TextField(verbose_name=_("Conteúdo"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))
    indexed_at = models.DateTimeField(auto_now=True, verbose_name=_("Indexado em"))

    class Meta:
        verbose_name = _("Índice de Busca")
        verbose_name_plural = _("Índices de Busca")
        unique_together = ["content_type", "object_id"]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"{self.content_type}:{self.object_id}"
