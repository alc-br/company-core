"""URL configuration for usage app."""

from rest_framework.routers import DefaultRouter
from apps.usage.views import UsageRecordViewSet

router = DefaultRouter()
router.register(r'records', UsageRecordViewSet, basename='usage-record')

urlpatterns = router.urls
