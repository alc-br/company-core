import logging
from django.core.files.storage import default_storage
from apps.common.exceptions import ServiceException

logger = logging.getLogger(__name__)


class StorageService:
    """Service for file upload, download, and management."""

    @staticmethod
    def upload_file(key, data, content_type=None, organization=None, uploaded_by=None):
        """Upload a file to storage.

        Args:
            key: file path/key in storage
            data: file-like object or bytes
            content_type: MIME type
            organization: Organization object
            uploaded_by: User object

        Returns:
            dict with file info (key, size, url)
        """
        try:
            saved_path = default_storage.save(key, data)

            # Calculate size
            size = 0
            if hasattr(data, "size"):
                size = data.size
            elif isinstance(data, bytes):
                size = len(data)

            from apps.storage.models import StoredObject
            stored = StoredObject.objects.create(
                key=saved_path,
                bucket=default_storage.bucket_name if hasattr(default_storage, "bucket_name") else "default",
                size=size,
                content_type=content_type or "",
                uploaded_by=uploaded_by,
                organization=organization,
            )
            logger.info(f"File uploaded: {saved_path} ({size} bytes)")
            return {
                "key": stored.key,
                "size": stored.size,
                "id": stored.id,
                "url": default_storage.url(saved_path) if hasattr(default_storage, "url") else None,
            }
        except Exception as e:
            logger.error(f"Upload failed for key {key}: {e}")
            raise ServiceException(f"Upload failed: {e}", code="upload_error")

    @staticmethod
    def download_file(key):
        """Download a file from storage.

        Args:
            key: file path/key in storage

        Returns:
            File-like object
        """
        if not default_storage.exists(key):
            raise ServiceException("File not found", code="file_not_found")
        return default_storage.open(key, "rb")

    @staticmethod
    def delete_file(key, organization=None):
        """Soft-delete a stored object and the actual file.

        Args:
            key: file path/key in storage
            organization: Organization (for scoping)
        """
        from apps.storage.models import StoredObject
        if organization:
            stored = StoredObject.objects.filter(key=key, organization=organization).first()
        else:
            stored = StoredObject.objects.filter(key=key).first()

        if stored:
            try:
                if default_storage.exists(key):
                    default_storage.delete(key)
            except Exception as e:
                logger.warning(f"Failed to delete file {key}: {e}")
            stored.delete()
            logger.info(f"File deleted: {key}")

    @staticmethod
    def get_file_url(key):
        """Get the public URL for a file."""
        if default_storage.exists(key):
            return default_storage.url(key)
        return None
