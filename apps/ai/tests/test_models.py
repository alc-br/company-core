import pytest
from apps.ai.models import AIProviderConfig, AIModelConfig, AICallLog


class TestAIProviderConfig:
    def test_str(self):
        config = AIProviderConfig(display_name="OpenAI", provider_name=1)
        assert "OpenAI" in str(config)


class TestAIModelConfig:
    def test_str(self):
        provider = AIProviderConfig(display_name="OpenAI", provider_name=1)
        model = AIModelConfig(display_name="GPT-4", model_id="gpt-4", provider=provider)
        assert "GPT-4" in str(model)


class TestAICallLog:
    def test_str(self):
        log = AICallLog(provider_name="openai", model="gpt-4", tokens_input=100, tokens_output=50)
        assert "openai" in str(log)
        assert "150" in str(log)
