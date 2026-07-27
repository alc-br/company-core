from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model


class EmailAsUsernameAdapter(DefaultAccountAdapter):
    """Forces username to be the email address (Pegasus pattern)."""

    def save_user(self, request, user, form, commit=True):
        user.username = user.email
        return super().save_user(request, user, form, commit)

    def clean_username(self, username, shallow=False):
        # Allow any valid email as username
        return username.lower().strip()
