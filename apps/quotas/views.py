from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.quotas.selectors import get_all_quotas


app_name = "quotas"


@login_required
def list_quotas(request):
    quotas = get_all_quotas(request.tenant.id) if request.tenant else []
    return render(request, "quotas/list.html", {"quotas": quotas})

