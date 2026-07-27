from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.audit.models import AuditLog


app_name = "audit"


@login_required
def list_logs(request):
    qs = AuditLog.objects.filter(organization=request.tenant) if request.tenant else AuditLog.objects.none()
    logs = qs.order_by("-created_at")[:100]
    return render(request, "audit/logs.html", {"logs": logs})

