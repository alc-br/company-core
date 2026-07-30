import hashlib
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """UserManager that supports email as USERNAME_FIELD."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom user model following SaaS Pegasus pattern.
    Uses email as the primary identifier (via allauth adapter).
    """

    username = models.CharField(max_length=150, null=True, blank=True, editable=False)
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

    objects = CustomUserManager()

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
