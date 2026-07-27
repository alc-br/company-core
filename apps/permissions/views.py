from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.permissions.models import Permission, Role


app_name = "permissions"


@login_required
def list_permissions(request):
    permissions = Permission.objects.all()
    return render(request, "permissions/list.html", {"permissions": permissions})

@login_required
def list_roles(request):
    roles = Role.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "permissions/roles.html", {"roles": roles})

