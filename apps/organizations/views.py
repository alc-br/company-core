from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.organizations.models import Organization, Membership
from apps.organizations.services import OrganizationService
from apps.organizations.selectors import get_user_organizations, get_organization_members, get_pending_invitations

app_name = "organizations"


@login_required
def list_organizations(request):
    orgs = get_user_organizations(request.user.id)
    return render(request, "organizations/list.html", {"organizations": orgs})


@login_required
def create_organization(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            org = OrganizationService.create_organization(name=name, owner=request.user)
            return redirect("organizations:detail", org_id=org.id)
    return render(request, "organizations/create.html")


@login_required
def detail_organization(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    members = get_organization_members(org_id)
    invitations = get_pending_invitations(org_id)
    return render(request, "organizations/detail.html", {"organization": org, "members": members, "invitations": invitations})


@login_required
def switch_organization(request):
    if request.GET.get("org_id"):
        request.session["active_organization_id"] = request.GET["org_id"]
    from django.http import HttpResponse
    return HttpResponse("")


@login_required
def invite_member(request):
    if request.method == "POST":
        org_id = request.POST.get("organization_id")
        email = request.POST.get("email", "").strip()
        role = int(request.POST.get("role", 3))
        org = get_object_or_404(Organization, id=org_id)
        try:
            OrganizationService.invite_member(org, email, role, invited_by=request.user)
        except Exception:
            pass
        return redirect("organizations:detail", org_id=org_id)
    return render(request, "organizations/invite.html")
