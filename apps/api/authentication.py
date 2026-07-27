import hashlib
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.api.models import APIKey
from django.utils import timezone


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header[7:]
        if not token.startswith("cc_live_"):
            return None
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            key_obj = APIKey.objects.select_related("user", "organization").get(
                key_hash=key_hash, is_active=True
            )
            if key_obj.expires_at and key_obj.expires_at < timezone.now():
                raise AuthenticationFailed("API key expired")
            key_obj.last_used_at = timezone.now()
            key_obj.save(update_fields=["last_used_at"])
            return (key_obj.user, {"organization": key_obj.organization, "api_key": key_obj})
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")
