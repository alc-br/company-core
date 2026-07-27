from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.settings.models import TenantSetting


app_name = "settings"


@login_required
def view_settings(request):
    if not request.tenant:
        return render(request, "settings/view.html", {"settings": []})
    settings_list = TenantSetting.objects.filter(organization=request.tenant)
    return render(request, "settings/view.html", {"settings": settings_list})

