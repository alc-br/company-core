from django.urls import path
from apps.health.views import HealthCheckView, ReadinessCheckView, LivenessCheckView

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health"),
    path("ready", ReadinessCheckView.as_view(), name="readiness"),
    path("live", LivenessCheckView.as_view(), name="liveness"),
]
