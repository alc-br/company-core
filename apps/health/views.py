from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok", "service": "company-core"})


class ReadinessCheckView(View):
    def get(self, request):
        checks = {}
        all_ok = True
        try:
            from django.db import connection
            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            all_ok = False
        try:
            from django.core.cache import cache
            cache.set("_health_check", "1", 10)
            checks["cache"] = "ok"
        except Exception as e:
            checks["cache"] = f"error: {str(e)}"
            all_ok = False
        status_code = 200 if all_ok else 503
        return JsonResponse({"status": "ok" if all_ok else "degraded", "checks": checks}, status=status_code)


class LivenessCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "alive"})
