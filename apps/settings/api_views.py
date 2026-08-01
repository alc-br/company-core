"""Endpoint /api/v1/settings consumido pela aba Organizacao/Alertas/Seguranca/
Privacidade de /app/configuracoes.

Usa TenantSetting (apps.settings) como bag chave/valor por organizacao —
'name' fica em Organization.name (fonte unica), o resto (tradeName, cnpj,
email, phone, logo, timezone, primaryColor, passwordMinLength,
auditRetentionDays e o blob 'settings' com os alertas) vira uma linha por
chave. Nada fica so na tela: tudo que o form tem, persiste de verdade.
"""
import json

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.settings.models import TenantSetting

MAX_LOGO_SIZE = 2 * 1024 * 1024
ALLOWED_LOGO_TYPES = {"image/png", "image/jpeg"}

SIMPLE_KEYS = [
    "trade_name", "cnpj", "email", "phone", "address", "logo", "timezone",
    "primary_color", "password_min_length", "audit_retention_days",
]


def _settings_dict(org):
    rows = TenantSetting.objects.filter(organization=org)
    return {row.key: row.value for row in rows}


def _active_sessions(user):
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    sessions = []
    for s in Session.objects.filter(expire_date__gte=timezone.now()):
        data = s.get_decoded()
        if str(data.get("_auth_user_id")) == str(user.id):
            sessions.append({
                "id": s.session_key[:8],
                "expires_at": s.expire_date,
            })
    return sessions


class SettingsView(TenantAPIView):
    def get(self, request):
        org = request.tenant
        kv = _settings_dict(org)
        raw_settings = kv.get("settings")
        try:
            nested = json.loads(raw_settings) if raw_settings else {}
        except ValueError:
            nested = {}

        return Response({
            "name": org.name,
            "trade_name": kv.get("trade_name", ""),
            "cnpj": kv.get("cnpj", ""),
            "email": kv.get("email", ""),
            "phone": kv.get("phone", ""),
            "address": kv.get("address", ""),
            "logo": kv.get("logo") or None,
            "timezone": kv.get("timezone", "America/Sao_Paulo"),
            "primary_color": kv.get("primary_color", "#2563eb"),
            "password_min_length": int(kv.get("password_min_length", 8)),
            "audit_retention_days": int(kv.get("audit_retention_days", 365)),
            # Ausente = organizacao criada antes deste recurso existir — nao forcamos
            # onboarding retroativo. So fica false quando setado explicitamente na criacao.
            "onboarding_completed": kv.get("onboarding_completed", "true") == "true",
            "settings": nested,
            "sessions": _active_sessions(request.user),
        })

    def put(self, request):
        org = request.tenant
        body = request.data

        if "name" in body and (body["name"] or "").strip():
            org.name = body["name"].strip()
            org.save(update_fields=["name", "updated_at"])

        for key in SIMPLE_KEYS:
            if key not in body:
                continue
            TenantSetting.objects.update_or_create(
                organization=org, key=key, environment="production",
                defaults={"value": str(body[key] if body[key] is not None else "")},
            )

        if "settings" in body and isinstance(body["settings"], dict):
            TenantSetting.objects.update_or_create(
                organization=org, key="settings", environment="production",
                defaults={"value": json.dumps(body["settings"])},
            )

        if "onboarding_completed" in body:
            TenantSetting.objects.update_or_create(
                organization=org, key="onboarding_completed", environment="production",
                defaults={"value": "true" if body["onboarding_completed"] else "false"},
            )

        return self.get(request)


def _public_storage_url(internal_url, request):
    """Reescreve a URL assinada do MinIO (rede interna docker) para o path
    publico /storage/ exposto pelo nginx — mesmo padrao usado em
    apps/radar_documents/serializers.py."""
    from django.conf import settings

    internal = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    if internal and internal_url and internal_url.startswith(internal):
        base = request.build_absolute_uri("/storage/")
        return base.rstrip("/") + "/" + internal_url[len(internal):].lstrip("/")
    return internal_url


class LogoUploadView(TenantAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "Arquivo obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        if file_obj.content_type not in ALLOWED_LOGO_TYPES:
            return Response({"error": "Envie um arquivo PNG ou JPG."}, status=status.HTTP_400_BAD_REQUEST)
        if file_obj.size > MAX_LOGO_SIZE:
            return Response({"error": "Arquivo maior que 2MB."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.storage.services import StorageService

        org = request.tenant
        key = f"org-{org.id}/logo/{file_obj.name}"
        stored = StorageService.upload_file(
            key=key, data=file_obj, content_type=file_obj.content_type,
            organization=org, uploaded_by=request.user,
        )
        url = _public_storage_url(stored.get("url"), request)

        TenantSetting.objects.update_or_create(
            organization=org, key="logo", environment="production",
            defaults={"value": url or ""},
        )
        return Response({"logo": url}, status=status.HTTP_201_CREATED)
