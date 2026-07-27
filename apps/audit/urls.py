from django.urls import path
from apps.audit import views as audit_views

app_name = "audit"

urlpatterns = [
    path('', audit_views.list_logs, name='logs'),
]
