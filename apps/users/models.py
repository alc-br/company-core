import hashlib
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Custom user model following SaaS Pegasus pattern.
    Uses email as the primary identifier (via allauth adapter).
    """

    email = models.EmailField(_("email address"), unique=True, max_length=255)
    avatar = models.ImageField(
        upload_to="profile-pictures/",
        blank=True,
        null=True,
        verbose_name=_("Avatar"),
        help_text=_("Profile picture"),
    )
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    timezone = models.CharField(
        max_length=50,
        default="America/Sao_Paulo",
        verbose_name=_("Timezone"),
    )
    language = models.CharField(
        max_length=10,
        default="pt-br",
        verbose_name=_("Language"),
    )

    # Email as username field (used by allauth EmailAsUsernameAdapter)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        """Return the full name or email as display name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    @property
    def avatar_url(self):
        """Return avatar URL or a Gravatar fallback."""
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return f"https://www.gravatar.com/avatar/{self.gravatar_id}?s=128&d=mp"

    @property
    def gravatar_id(self):
        """Return MD5 hash of the email for Gravatar."""
        return hashlib.md5(self.email.lower().strip().encode()).hexdigest()

    @property
    def has_verified_email(self):
        """Check if the user has verified their email via allauth."""
        from allauth.account.models import EmailAddress
        return EmailAddress.objects.filter(
            user=self, email=self.email, verified=True
        ).exists()
