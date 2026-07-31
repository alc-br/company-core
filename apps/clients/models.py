from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin, SoftDeleteMixin


class Department(TenantMixin, TimestampMixin):
    """Departamento operacional do escritório (Fiscal, Pessoal, Contábil, ...)."""

    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    color = models.CharField(max_length=20, blank=True, default="#2563eb", verbose_name=_("Cor"))
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
        verbose_name=_("Gestor"),
    )

    class Meta:
        verbose_name = _("Departamento")
        verbose_name_plural = _("Departamentos")
        ordering = ["name"]
        unique_together = ["organization", "name"]

    def __str__(self):
        return self.name


class Tag(TenantMixin, TimestampMixin):
    """Etiqueta livre reutilizável em clientes, tarefas e documentos."""

    name = models.CharField(max_length=60, verbose_name=_("Nome"))
    color = models.CharField(max_length=20, blank=True, default="#6b7280", verbose_name=_("Cor"))

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]
        unique_together = ["organization", "name"]

    def __str__(self):
        return self.name


class ClientCompany(TenantMixin, TimestampMixin, SoftDeleteMixin):
    """Empresa-cliente atendida pelo escritório."""

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_SUSPENDED = "suspended"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Rascunho")),
        (STATUS_ACTIVE, _("Ativo")),
        (STATUS_SUSPENDED, _("Suspenso")),
        (STATUS_ARCHIVED, _("Arquivado")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Razão social"))
    trade_name = models.CharField(max_length=255, blank=True, verbose_name=_("Nome fantasia"))
    cnpj = models.CharField(max_length=18, blank=True, verbose_name=_("CNPJ"))
    ie = models.CharField(max_length=30, blank=True, verbose_name=_("Inscrição estadual"))
    im = models.CharField(max_length=30, blank=True, verbose_name=_("Inscrição municipal"))
    cnae = models.CharField(max_length=20, blank=True, verbose_name=_("CNAE principal"))
    tax_regime = models.CharField(max_length=60, blank=True, verbose_name=_("Regime tributário"))
    company_size = models.CharField(max_length=30, blank=True, verbose_name=_("Porte"))
    segment = models.CharField(max_length=100, blank=True, verbose_name=_("Segmento"))
    open_date = models.DateField(null=True, blank=True, verbose_name=_("Data de abertura"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name=_("Status"))
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_clients",
        verbose_name=_("Responsável"),
    )
    email = models.EmailField(blank=True, verbose_name=_("E-mail"))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefone"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Endereço"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("Cidade"))
    state = models.CharField(max_length=2, blank=True, verbose_name=_("UF"))
    zip_code = models.CharField(max_length=10, blank=True, verbose_name=_("CEP"))
    notes = models.TextField(blank=True, verbose_name=_("Observações internas"))
    portal_access = models.BooleanField(default=False, verbose_name=_("Acesso ao portal"))
    service_start_date = models.DateField(null=True, blank=True, verbose_name=_("Início do atendimento"))
    tags = models.ManyToManyField(Tag, blank=True, related_name="clients", verbose_name=_("Tags"))

    class Meta:
        verbose_name = _("Empresa-cliente")
        verbose_name_plural = _("Empresas-clientes")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "cnpj"]),
            models.Index(fields=["organization", "name"]),
        ]

    def __str__(self):
        return self.trade_name or self.name


class ClientContact(TenantMixin, TimestampMixin):
    """Pessoa de contato de uma empresa-cliente, com acesso opcional ao portal."""

    client = models.ForeignKey(ClientCompany, on_delete=models.CASCADE, related_name="contacts", verbose_name=_("Cliente"))
    name = models.CharField(max_length=150, verbose_name=_("Nome"))
    email = models.EmailField(blank=True, verbose_name=_("E-mail"))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefone"))
    role = models.CharField(max_length=100, blank=True, verbose_name=_("Cargo"))
    has_portal_access = models.BooleanField(default=False, verbose_name=_("Acesso ao portal"))
    password_hash = models.CharField(max_length=255, blank=True, verbose_name=_("Senha do portal (hash)"))
    notes = models.TextField(blank=True, verbose_name=_("Observações"))

    class Meta:
        verbose_name = _("Contato do cliente")
        verbose_name_plural = _("Contatos do cliente")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["client"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.client.name})"
