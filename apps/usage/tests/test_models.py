import pytest
from apps.usage.models import UsageRecord


class TestUsageRecord:
    def test_usage_record_creation(self):
        record = UsageRecord(metric_type=1, value=10, unit="requests")
        assert record.value == 10
        assert record.unit == "requests"
