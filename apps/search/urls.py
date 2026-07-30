"""URL configuration for search app."""

from rest_framework.routers import DefaultRouter
from apps.search.views import SearchIndexViewSet

router = DefaultRouter()
router.register(r'indices', SearchIndexViewSet, basename='search-index')

urlpatterns = router.urls
