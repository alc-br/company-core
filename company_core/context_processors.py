"""Context processors for Company Core templates."""
from django.conf import settings


def project_meta(request):
    """Inject project metadata into all templates."""
    return {"PROJECT": settings.PROJECT_METADATA}


def csrf_settings(request):
    """Expose CSRF settings to templates."""
    return {"CSRF_SETTINGS": {"USE_CSRF": True}}
