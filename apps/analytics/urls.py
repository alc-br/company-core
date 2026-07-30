"""URL configuration for analytics app."""

from rest_framework.routers import DefaultRouter
from apps.analytics.views import AnalyticsEventViewSet, AnalyticsAggregationViewSet

router = DefaultRouter()
router.register(r'events', AnalyticsEventViewSet, basename='analytics-event')
router.register(r'aggregations', AnalyticsAggregationViewSet, basename='analytics-aggregation')

urlpatterns = router.urls
