"""
WSGI config for Company Core project.

This module contains the WSGI callable for the Django project.
It is used by Gunicorn/uWSGI to serve the application.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "company_core.settings.base")

application = get_wsgi_application()
