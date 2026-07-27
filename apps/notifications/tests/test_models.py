import pytest
from apps.notifications.models import NotificationChannel, NotificationTemplate, NotificationLog


class TestNotificationChannel:
    def test_channel_creation(self):
        channel = NotificationChannel(name="email-primary", type=1)
        assert channel.name == "email-primary"

    def test_template_creation(self):
        template = NotificationTemplate(code="welcome_email", subject="Welcome")
        assert template.code == "welcome_email"

    def test_log_creation(self):
        log = NotificationLog(recipient="test@example.com", status="sent")
        assert log.recipient == "test@example.com"
