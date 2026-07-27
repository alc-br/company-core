import pytest
from apps.api.models import APIKey, PersonalAccessToken, ServiceAccount


class TestAPIKey:
    def test_api_key_generation(self):
        raw, key_hash, prefix = APIKey.generate_key()
        assert raw.startswith("cc_live_")
        assert prefix == raw[:12]
        assert len(key_hash) == 64

    def test_api_key_creation(self):
        key = APIKey(name="test-key", key_hash="abc123", prefix="cc_live_12")
        assert key.name == "test-key"

    def test_personal_access_token_creation(self):
        token = PersonalAccessToken(name="my-token", token_hash="hash123")
        assert token.name == "my-token"

    def test_service_account_creation(self):
        sa = ServiceAccount(name="ci-bot", token_hash="hash456")
        assert sa.is_active is True
