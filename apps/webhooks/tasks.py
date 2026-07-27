from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_webhook_task(self, delivery_id):
    from apps.webhooks.models import WebhookDelivery
    from apps.webhooks.services import WebhookService

    try:
        delivery = WebhookDelivery.objects.get(id=delivery_id)
        WebhookService.deliver(delivery)
    except Exception as exc:
        self.retry(exc=exc)
