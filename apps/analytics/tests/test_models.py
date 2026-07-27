import pytest
from apps.analytics.models import AnalyticsEvent, AnalyticsAggregation


class TestAnalyticsEvent:
    def test_analytics_event_creation(self):
        event = AnalyticsEvent(event_type="page_view", module="dashboard")
        assert event.event_type == "page_view"
        assert event.module == "dashboard"

    def test_analytics_aggregation_creation(self):
        agg = AnalyticsAggregation(module="dashboard", metric="views", value=42.5)
        assert agg.value == 42.5
