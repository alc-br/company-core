from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin


class Template(TenantMixin, TimestampMixin):
    """Identidade logica de um template operacional.

    A estrutura editavel (etapas -> tarefas -> checklist -> documentos) fica
    em `stages` (JSON), espelhando exatamente como o frontend manipula essa
    arvore (ver TMP-03 na especificacao). Publicar cria um snapshot imutavel
    em TemplateVersion; o rascunho (`stages`) continua livre para editar.
    """

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Rascunho")),
        (STATUS_PUBLISHED, _("Publicado")),
        (STATUS_ARCHIVED, _("Arquivado")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    code = models.CharField(max_length=60, blank=True, verbose_name=_("Codigo interno"))
    description = models.TextField(blank=True, verbose_name=_("Descricao"))
    purpose = models.TextField(blank=True, verbose_name=_("Finalidade"))
    category = models.CharField(max_length=100, blank=True, verbose_name=_("Categoria"))
    color = models.CharField(max_length=20, blank=True, default="#2563eb", verbose_name=_("Cor"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name=_("Status"))
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="responsible_templates", verbose_name=_("Responsavel tecnico"),
    )
    department = models.ForeignKey(
        "clients.Department", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="templates", verbose_name=_("Departamento"),
    )
    instructions = models.TextField(blank=True, verbose_name=_("Instrucoes"))
    warning = models.TextField(blank=True, verbose_name=_("Aviso"))
    default_periodicity = models.CharField(max_length=30, blank=True, verbose_name=_("Periodicidade padrao"))
    variables = models.JSONField(default=list, blank=True, verbose_name=_("Variaveis"))
    stages = models.JSONField(default=list, blank=True, verbose_name=_("Etapas (rascunho)"))
    current_version = models.PositiveIntegerField(default=0, verbose_name=_("Versao atual publicada"))

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "category"]),
        ]

    def __str__(self):
        return self.name


class TemplateVersion(TenantMixin, TimestampMixin):
    """Snapshot imutavel de um template no momento da publicacao."""

    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="versions", verbose_name=_("Template"))
    version_number = models.PositiveIntegerField(verbose_name=_("Numero da versao"))
    name = models.CharField(max_length=255, verbose_name=_("Nome (no momento da publicacao)"))
    stages_snapshot = models.JSONField(default=list, verbose_name=_("Etapas (snapshot)"))
    metadata_snapshot = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados (snapshot)"))
    is_current = models.BooleanField(default=True, verbose_name=_("E a versao vigente"))
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="published_template_versions", verbose_name=_("Publicado por"),
    )
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Publicado em"))

    class Meta:
        verbose_name = _("Versao de template")
        verbose_name_plural = _("Versoes de template")
        ordering = ["-version_number"]
        unique_together = ["template", "version_number"]

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"


class TemplateApplication(TenantMixin, TimestampMixin):
    """Aplicacao de uma versao publicada de template a uma empresa-cliente."""

    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, _("Ativa")),
        (STATUS_COMPLETED, _("Concluida")),
        (STATUS_CANCELLED, _("Cancelada")),
    ]

    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="applications", verbose_name=_("Template"))
    template_version = models.ForeignKey(
        TemplateVersion, on_delete=models.PROTECT, related_name="applications", verbose_name=_("Versao aplicada"),
    )
    client = models.ForeignKey(
        "clients.ClientCompany", on_delete=models.CASCADE, related_name="template_applications", verbose_name=_("Cliente"),
    )
    base_date = models.DateField(verbose_name=_("Data-base"))
    variables = models.JSONField(default=dict, blank=True, verbose_name=_("Variaveis informadas"))
    role_mappings = models.JSONField(default=dict, blank=True, verbose_name=_("Mapeamento de papeis/departamentos"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name=_("Status"))
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="template_applications_made", verbose_name=_("Aplicado por"),
    )

    class Meta:
        verbose_name = _("Aplicacao de template")
        verbose_name_plural = _("Aplicacoes de template")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "client"]),
            models.Index(fields=["organization", "status"]),
        ]

    def __str__(self):
        return f"{self.template.name} -> {self.client.name}"
