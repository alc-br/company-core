"""Celery configuration for Company Core."""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "company_core.settings.base")

app = Celery("company_core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
