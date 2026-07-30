"""URL configuration for jobs app."""

from rest_framework.routers import DefaultRouter
from apps.jobs.views import JobViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')

urlpatterns = router.urls
