import pytest
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery


class TestWebhookEndpoint:
    def test_endpoint_creation(self):
        endpoint = WebhookEndpoint(url="https://example.com/webhook")
        assert endpoint.url == "https://example.com/webhook"
        assert endpoint.is_active is True

    def test_delivery_creation(self):
        delivery = WebhookDelivery(event_type="user.created", status="pending")
        assert delivery.event_type == "user.created"
        assert delivery.attempts == 0
