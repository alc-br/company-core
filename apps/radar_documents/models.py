from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin


class DocumentType(TenantMixin, TimestampMixin):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    category = models.CharField(max_length=100, blank=True, verbose_name=_("Categoria"))
    allowed_formats = models.CharField(max_length=255, blank=True, verbose_name=_("Formatos aceitos"))
    max_size_mb = models.PositiveIntegerField(default=25, verbose_name=_("Tamanho maximo (MB)"))
    validity_days = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Prazo de validade (dias)"))

    class Meta:
        verbose_name = _("Tipo de documento")
        verbose_name_plural = _("Tipos de documento")
        ordering = ["name"]
        unique_together = ["organization", "name"]

    def __str__(self):
        return self.name


class DocumentRequest(TenantMixin, TimestampMixin):
    STATUS_SOLICITADO = "solicitado"
    STATUS_RECEBIDO = "recebido"
    STATUS_CHOICES = [
        (STATUS_SOLICITADO, _("Solicitado")),
        (STATUS_RECEBIDO, _("Recebido")),
    ]

    client = models.ForeignKey("clients.ClientCompany", on_delete=models.CASCADE, related_name="document_requests", verbose_name=_("Cliente"))
    title = models.CharField(max_length=255, verbose_name=_("Titulo"))
    instructions = models.TextField(blank=True, verbose_name=_("Instrucoes"))
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Prazo"))
    accepted_formats = models.CharField(max_length=255, blank=True, verbose_name=_("Formatos aceitos"))
    reminder_1d = models.BooleanField(default=False)
    reminder_3d = models.BooleanField(default=False)
    reminder_7d = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SOLICITADO, verbose_name=_("Status"))
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="document_requests_made", verbose_name=_("Solicitado por"),
    )

    class Meta:
        verbose_name = _("Solicitacao de documento")
        verbose_name_plural = _("Solicitacoes de documento")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "client", "status"])]

    def __str__(self):
        return f"{self.title} ({self.client.name})"


class Document(TenantMixin, TimestampMixin):
    STATUS_SOLICITADO = "solicitado"
    STATUS_RECEBIDO = "recebido"
    STATUS_EM_ANALISE = "em_análise"
    STATUS_APROVADO = "aprovado"
    STATUS_REJEITADO = "rejeitado"
    STATUS_ARQUIVADO = "arquivado"
    STATUS_CHOICES = [
        (STATUS_SOLICITADO, _("Solicitado")),
        (STATUS_RECEBIDO, _("Recebido")),
        (STATUS_EM_ANALISE, _("Em analise")),
        (STATUS_APROVADO, _("Aprovado")),
        (STATUS_REJEITADO, _("Rejeitado")),
        (STATUS_ARQUIVADO, _("Arquivado")),
    ]

    client = models.ForeignKey("clients.ClientCompany", on_delete=models.CASCADE, related_name="documents", verbose_name=_("Cliente"))
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="documents", verbose_name=_("Tipo"))
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEBIDO, verbose_name=_("Status"))
    competence = models.CharField(max_length=20, blank=True, verbose_name=_("Competencia"))
    validity_date = models.DateField(null=True, blank=True, verbose_name=_("Validade"))
    notes = models.TextField(blank=True, verbose_name=_("Observacoes"))
    stored_object = models.ForeignKey(
        "storage.StoredObject", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", verbose_name=_("Arquivo"),
    )
    task = models.ForeignKey(
        "radar_tasks.Task", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="linked_documents", verbose_name=_("Tarefa vinculada"),
    )
    request = models.ForeignKey(
        DocumentRequest, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fulfillments", verbose_name=_("Solicitacao de origem"),
    )
    rejection_reason = models.TextField(blank=True, verbose_name=_("Motivo da rejeicao"))

    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "client", "status"])]

    def __str__(self):
        return self.name
