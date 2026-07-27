import pytest
from apps.quotas.models import QuotaDefinition, QuotaAllocation


class TestQuotaDefinition:
    def test_str(self):
        qd = QuotaDefinition(code="ai_prompts", name="AI Prompts", unit="requests")
        assert "AI Prompts" in str(qd)


class TestQuotaAllocation:
    def test_remaining(self):
        qa = QuotaAllocation(limit=100, used=30)
        assert qa.remaining == 70
        assert qa.is_exceeded is False
