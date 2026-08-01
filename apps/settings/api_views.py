"""Endpoint /api/v1/settings consumido pela aba Organizacao/Alertas/Seguranca/
Privacidade de /app/configuracoes.

Usa TenantSetting (apps.settings) como bag chave/valor por organizacao —
'name' fica em Organization.name (fonte unica), o resto (tradeName, cnpj,
email, phone, logo, timezone, primaryColor, passwordMinLength,
auditRetentionDays e o blob 'settings' com os alertas) vira uma linha por
chave. Nada fica so na tela: tudo que o form tem, persiste de verdade.
"""
import json

from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.settings.models import TenantSetting

SIMPLE_KEYS = ["trade_name", "cnpj", "email", "phone", "logo", "timezone", "primary_color", "password_min_length", "audit_retention_days"]


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
            "logo": kv.get("logo") or None,
            "timezone": kv.get("timezone", "America/Sao_Paulo"),
            "primary_color": kv.get("primary_color", "#2563eb"),
            "password_min_length": int(kv.get("password_min_length", 8)),
            "audit_retention_days": int(kv.get("audit_retention_days", 365)),
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

        return self.get(request)
