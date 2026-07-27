from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.ai.models import AIProviderConfig, AICallLog


app_name = "ai"


@login_required
def list_providers(request):
    providers = AIProviderConfig.objects.all()
    return render(request, "ai/providers.html", {"providers": providers})

@login_required
def call_logs(request):
    qs = AICallLog.objects.filter(organization=request.tenant) if request.tenant else AICallLog.objects.none()
    logs = qs.order_by("-created_at")[:50]
    return render(request, "ai/call_logs.html", {"logs": logs})

