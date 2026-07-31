from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin


class Announcement(TenantMixin, TimestampMixin):
    """Comunicado do escritorio para os clientes (gerenciado por staff/admin)."""

    title = models.CharField(max_length=255, verbose_name=_("Titulo"))
    body = models.TextField(verbose_name=_("Conteudo"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="announcements", verbose_name=_("Autor"),
    )
    clients = models.ManyToManyField(
        "clients.ClientCompany", blank=True, related_name="announcements",
        verbose_name=_("Clientes (vazio = todos)"),
    )
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Publicado em"))

    class Meta:
        verbose_name = _("Comunicado")
        verbose_name_plural = _("Comunicados")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
