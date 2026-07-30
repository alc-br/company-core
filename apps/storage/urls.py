"""URL configuration for storage app."""

from rest_framework.routers import DefaultRouter
from apps.storage.views import StorageBackendConfigViewSet, StoredObjectViewSet

router = DefaultRouter()
router.register(r'backends', StorageBackendConfigViewSet, basename='storage-backend')
router.register(r'objects', StoredObjectViewSet, basename='stored-object')

urlpatterns = router.urls
