import uuid
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import MembershipRole, MembershipStatus, InvitationStatus
from apps.common.helpers import generate_unique_slug


class Organization(TimestampMixin):
    """Represents a tenant/organization in the multi-tenant system."""

    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("Slug"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_organizations",
        verbose_name=_("Proprietário"),
    )
    status = models.IntegerField(
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
        verbose_name=_("Status"),
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))

    class Meta:
        verbose_name = _("Organização")
        verbose_name_plural = _("Organizações")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Organization, self.name.lower().replace(" ", "-"))
        super().save(*args, **kwargs)


class Membership(TimestampMixin):
    """Links users to organizations with roles."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("Usuário"),
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("Organização"),
    )
    role = models.IntegerField(
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
        verbose_name=_("Papel"),
    )
    status = models.IntegerField(
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
        verbose_name=_("Status"),
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations_made",
        verbose_name=_("Convidado por"),
    )
    department = models.ForeignKey(
        "clients.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        verbose_name=_("Departamento"),
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Entrou em"),
    )

    class Meta:
        verbose_name = _("Membro")
        verbose_name_plural = _("Membros")
        ordering = ["-created_at"]
        unique_together = ["user", "organization"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.get_role_display()})"


class Invitation(TimestampMixin):
    """Invitation to join an organization."""

    email = models.EmailField(verbose_name=_("Email"))
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name=_("Organização"),
    )
    role = models.IntegerField(
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
        verbose_name=_("Papel"),
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name=_("Token"))
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Aceito em"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expira em"))
    status = models.IntegerField(
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
        verbose_name=_("Status"),
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
        verbose_name=_("Convidado por"),
    )

    class Meta:
        verbose_name = _("Convite")
        verbose_name_plural = _("Convites")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "organization"]),
            models.Index(fields=["token"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Convite para {self.email} ({self.organization.name})"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()
