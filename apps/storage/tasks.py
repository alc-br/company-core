import logging
from celery import shared_task
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_orphaned_files_task(self):
    """Find and clean up stored objects without database references."""
    from apps.storage.models import StoredObject

    try:
        orphaned_keys = []
        orphaned_count = 0

        # Find all stored objects and check if their files still exist
        # Also find files in storage that have no database reference
        stored_objects = StoredObject.objects.all()
        for obj in stored_objects:
            if not default_storage.exists(obj.key):
                # Database record has no backing file — orphaned record
                orphaned_keys.append(obj.key)
                obj.delete()
                orphaned_count += 1
                logger.info(f"Deleted orphaned database record for key: {obj.key}")

        # Check for files in storage without database records
        try:
            all_keys = list(default_storage.listdir(""))[1] if hasattr(default_storage, "listdir") else []
        except (NotImplementedError, Exception):
            all_keys = []

        known_keys = set(StoredObject.objects.values_list("key", flat=True))
        for key in all_keys:
            if key not in known_keys:
                try:
                    default_storage.delete(key)
                    orphaned_count += 1
                    logger.info(f"Deleted orphaned file from storage: {key}")
                except Exception as e:
                    logger.warning(f"Could not delete orphaned file {key}: {e}")

        logger.info(f"Orphaned file cleanup complete: {orphaned_count} items cleaned")
        return {"cleaned_count": orphaned_count}
    except Exception as exc:
        logger.error(f"Failed to cleanup orphaned files: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_download_url_task(self, file_key, expires_in=3600):
    """Generate a temporary download URL."""
    from apps.storage.models import StoredObject
    from apps.common.exceptions import NotFoundException

    try:
        stored = StoredObject.objects.filter(key=file_key).first()
        if not stored:
            logger.warning(f"Stored object not found for key: {file_key}")
            return None

        url = None
        if hasattr(default_storage, "url"):
            url = default_storage.url(file_key)

        # If using S3-compatible storage, generate a presigned URL
        if not url or "blob:" in str(url):
            try:
                url = default_storage.generate_presigned_url(
                    file_key, expires_in=expires_in
                ) if hasattr(default_storage, "generate_presigned_url") else None
            except Exception as e:
                logger.warning(f"Could not generate presigned URL for {file_key}: {e}")

        result = {
            "key": file_key,
            "url": url,
            "expires_in": expires_in,
        }
        logger.info(f"Download URL generated for key: {file_key}")
        return result
    except Exception as exc:
        logger.error(f"Failed to generate download URL for {file_key}: {exc}")
        self.retry(exc=exc)
