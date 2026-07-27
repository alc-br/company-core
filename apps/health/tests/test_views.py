import pytest
from django.test import RequestFactory
from apps.health.views import HealthCheckView, ReadinessCheckView, LivenessCheckView


class TestHealthCheckView:
    def test_health(self):
        view = HealthCheckView.as_view()
        request = RequestFactory().get("/")
        response = view(request)
        assert response.status_code == 200


class TestLivenessCheckView:
    def test_liveness(self):
        view = LivenessCheckView.as_view()
        request = RequestFactory().get("/")
        response = view(request)
        assert response.status_code == 200
