import pytest
from apps.integrations.models import Integration, IntegrationLog


class TestIntegration:
    def test_integration_creation(self):
        integration = Integration(name="stripe", integration_type="payment")
        assert integration.name == "stripe"
        assert integration.status == "active"

    def test_integration_log_creation(self):
        log = IntegrationLog(action="sync", status="success", duration_ms=150)
        assert log.duration_ms == 150
