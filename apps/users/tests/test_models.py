import pytest
from apps.users.models import CustomUser


class TestCustomUser:
    def test_str_with_email_only(self):
        user = CustomUser(email="test@example.com")
        assert "test@example.com" in str(user)

    def test_str_with_names(self):
        user = CustomUser(email="test@example.com", first_name="John", last_name="Doe")
        assert "John Doe" in str(user)

    def test_has_avatar_url(self):
        user = CustomUser(email="test@example.com")
        assert hasattr(user, "avatar_url")

    def test_has_gravatar_id(self):
        user = CustomUser(email="test@example.com")
        assert user.gravatar_id is not None
