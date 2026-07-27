from django.urls import path
from apps.ai import views as ai_views

app_name = "ai"

urlpatterns = [
    path('providers/', ai_views.list_providers, name='providers'),
    path('logs/', ai_views.call_logs, name='logs'),
]
