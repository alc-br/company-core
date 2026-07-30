from django.urls import path
from apps.web.views import dashboard_view

app_name = "web"

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
]
