from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
import hashlib
import uuid


class APIKey(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    key_hash = models.CharField(max_length=255, unique=True, verbose_name=_("Key Hash"))
    prefix = models.CharField(max_length=12, verbose_name=_("Prefix"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name=_("Usuário"),
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name=_("Organização"),
    )
    scopes = models.JSONField(default=list, blank=True, verbose_name=_("Scopes"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Último Uso"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expira em"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_api_keys",
        verbose_name=_("Criado por"),
    )

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    @classmethod
    def generate_key(cls):
        raw = f"cc_live_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw.encode()).hexdigest()
        prefix = raw[:12]
        return raw, key_hash, prefix


class PersonalAccessToken(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    token_hash = models.CharField(max_length=255, unique=True, verbose_name=_("Token Hash"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="personal_tokens",
        verbose_name=_("Usuário"),
    )
    scopes = models.JSONField(default=list, blank=True, verbose_name=_("Scopes"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expira em"))

    class Meta:
        verbose_name = _("Personal Access Token")
        verbose_name_plural = _("Personal Access Tokens")

    def __str__(self):
        return self.name


class ServiceAccount(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    token_hash = models.CharField(max_length=255, unique=True, verbose_name=_("Token Hash"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="service_accounts",
        verbose_name=_("Organização"),
    )
    permissions = models.JSONField(default=list, blank=True, verbose_name=_("Permissões"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Service Account")
        verbose_name_plural = _("Service Accounts")

    def __str__(self):
        return self.name
