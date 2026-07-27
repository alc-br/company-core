from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """Middleware that injects the active tenant into the request."""

    def process_request(self, request):
        if request.user.is_authenticated:
            org_id = request.session.get("active_organization_id")
            if org_id:
                from apps.organizations.models import Organization
                try:
                    request.tenant = Organization.objects.get(
                        id=org_id,
                        memberships__user=request.user,
                        memberships__status=1,  # ACTIVE
                    )
                except Organization.DoesNotExist:
                    request.tenant = None
            else:
                from apps.organizations.selectors import get_user_organizations
                orgs = get_user_organizations(request.user.id)
                request.tenant = orgs.first()
        else:
            request.tenant = None
        return None
