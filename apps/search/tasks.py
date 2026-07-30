import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def reindex_all_task(self):
    """Reindex all searchable content."""
    from apps.search.models import SearchIndex
    from django.apps import apps
    from django.contrib.contenttypes.models import ContentType

    try:
        models_to_index = []
        all_models = apps.get_models()

        for model in all_models:
            if not model._meta.abstract and hasattr(model, "_search_fields"):
                models_to_index.append(model)

        if not models_to_index:
            logger.info("No models with _search_fields found for indexing")
            return {"indexed": 0, "models": 0}

        total_indexed = 0
        for model in models_to_index:
            search_fields = model._search_fields
            ct = ContentType.objects.get_for_model(model)
            instances = model.objects.all()

            for instance in instances:
                content_parts = []
                for field in search_fields:
                    value = getattr(instance, field, "")
                    if value:
                        content_parts.append(str(value))

                content = " ".join(content_parts)
                metadata = {
                    "app_label": model._meta.app_label,
                    "model_name": model._meta.model_name,
                    "search_fields": search_fields,
                }

                SearchIndex.objects.update_or_create(
                    content_type=f"{ct.app_label}.{ct.model}",
                    object_id=str(instance.pk),
                    defaults={
                        "content": content,
                        "metadata": metadata,
                    },
                )
                total_indexed += 1

        logger.info(f"Reindex complete: {total_indexed} objects across {len(models_to_index)} models")
        return {"indexed": total_indexed, "models": len(models_to_index)}
    except Exception as exc:
        logger.error(f"Failed to reindex all content: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def index_model_task(self, app_label, model_name, object_ids):
    """Index specific model instances."""
    from apps.search.models import SearchIndex
    from django.apps import apps

    try:
        model = apps.get_model(app_label, model_name)
        search_fields = getattr(model, "_search_fields", ["id", "name"])

        if isinstance(object_ids, str):
            object_ids = [object_ids]

        indexed_count = 0
        for obj_id in object_ids:
            try:
                instance = model.objects.get(pk=obj_id)
            except model.DoesNotExist:
                logger.warning(f"Object {app_label}.{model_name}:{obj_id} not found for indexing")
                continue

            content_parts = []
            for field in search_fields:
                value = getattr(instance, field, "")
                if value:
                    content_parts.append(str(value))

            content = " ".join(content_parts)
            metadata = {
                "app_label": app_label,
                "model_name": model_name,
                "search_fields": search_fields,
            }

            SearchIndex.objects.update_or_create(
                content_type=f"{app_label}.{model_name}",
                object_id=str(obj_id),
                defaults={
                    "content": content,
                    "metadata": metadata,
                },
            )
            indexed_count += 1

        logger.info(
            f"Indexed {indexed_count}/{len(object_ids)} objects of "
            f"{app_label}.{model_name}"
        )
        return {"indexed": indexed_count, "total": len(object_ids)}
    except LookupError as e:
        logger.error(f"Model {app_label}.{model_name} not found: {e}")
        return None
    except Exception as exc:
        logger.error(f"Failed to index model {app_label}.{model_name}: {exc}")
        self.retry(exc=exc)
