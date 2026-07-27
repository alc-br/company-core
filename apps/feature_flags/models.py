from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class FeatureFlag(TimestampMixin):
    """Feature flag that can be toggled per organization, user, or environment."""

    code = models.CharField(max_length=255, unique=True, verbose_name=_("Código"))
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    is_active = models.BooleanField(default=False, verbose_name=_("Ativo Globalmente"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Criado por"),
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="feature_flags_direct",
        verbose_name=_("Usuários"),
        help_text=_("Users for whom this flag is active (waffle compatibility)"),
    )
    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="feature_flags",
        verbose_name=_("Grupos"),
    )

    class Meta:
        verbose_name = _("Feature Flag")
        verbose_name_plural = _("Feature Flags")
        ordering = ["code"]
        permissions = [
            ("can_view_featureflag", "Can view feature flag"),
        ]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} ({'ON' if self.is_active else 'OFF'})"


class FeatureFlagAssignment(TimestampMixin):
    """Assignment of a feature flag to a specific context (org, user, environment)."""

    flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Flag"),
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feature_flags",
        verbose_name=_("Organização"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feature_flags",
        verbose_name=_("Usuário"),
    )
    environment = models.CharField(
        max_length=50,
        default="production",
        verbose_name=_("Ambiente"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Atribuição de Feature Flag")
        verbose_name_plural = _("Atribuições de Feature Flags")
        indexes = [
            models.Index(fields=["flag", "organization", "is_active"]),
            models.Index(fields=["flag", "user", "is_active"]),
        ]

    def __str__(self):
        target = (
            self.organization.name
            if self.organization
            else self.user.email
            if self.user
            else "global"
        )
        return f"{self.flag.code} -> {target}"
