"""
ASGI config for Company Core project.

This module contains the ASGI callable for the Django project.
It is used by Daphne/Uvicorn to serve async applications.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "company_core.settings.base")

application = get_asgi_application()
