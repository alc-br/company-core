import pytest
from apps.storage.models import StorageBackendConfig, StoredObject


class TestStorageBackendConfig:
    def test_backend_creation(self):
        backend = StorageBackendConfig(name="s3-primary", backend_type=1)
        assert backend.name == "s3-primary"

    def test_stored_object_creation(self):
        obj = StoredObject(key="uploads/file.pdf", bucket="my-bucket", content_type="application/pdf")
        assert obj.key == "uploads/file.pdf"
        assert obj.content_type == "application/pdf"
