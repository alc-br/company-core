from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.storage.models import StoredObject


app_name = "storage"


@login_required
def list_files(request):
    qs = StoredObject.objects.filter(organization=request.tenant) if request.tenant else StoredObject.objects.none()
    files = qs.order_by("-created_at")[:50]
    return render(request, "storage/list.html", {"files": files})

