import hashlib
import hmac
import logging
import time
import httpx

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for webhook delivery and management."""

    @staticmethod
    def deliver(delivery):
        """Deliver a webhook payload to the endpoint.

        Args:
            delivery: WebhookDelivery instance

        Returns:
            dict with status, response_code
        """
        import json
        endpoint = delivery.endpoint
        payload = delivery.payload

        # Build headers
        timestamp = str(int(time.time()))
        signature = WebhookService._sign_payload(
            endpoint.secret_encrypted or b"",
            payload,
            timestamp,
        )

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Event": delivery.event_type,
            "X-Webhook-Delivery": str(delivery.id),
        }

        try:
            response = httpx.post(
                endpoint.url,
                json=payload,
                headers=headers,
                timeout=30.0,
            )

            delivery.status = "success" if 200 <= response.status_code < 300 else "failed"
            delivery.response_code = response.status_code
            delivery.attempts += 1
            delivery.last_attempt_at = time.strftime("%Y-%m-%d %H:%M:%S")
            delivery.save(update_fields=["status", "response_code", "attempts", "last_attempt_at"])

            logger.info(
                f"Webhook delivered: {delivery.event_type} -> {endpoint.url} "
                f"(status={response.status_code})"
            )

            return {"status": delivery.status, "response_code": response.status_code}

        except httpx.TimeoutException:
            delivery.status = "failed"
            delivery.attempts += 1
            delivery.last_attempt_at = time.strftime("%Y-%m-%d %H:%M:%S")
            delivery.save(update_fields=["status", "attempts", "last_attempt_at"])
            logger.error(f"Webhook timeout: {delivery.event_type} -> {endpoint.url}")
            return {"status": "timeout", "response_code": None}

        except Exception as e:
            delivery.status = "failed"
            delivery.attempts += 1
            delivery.last_attempt_at = time.strftime("%Y-%m-%d %H:%M:%S")
            delivery.save(update_fields=["status", "attempts", "last_attempt_at"])
            logger.error(f"Webhook delivery failed: {e}")
            return {"status": "error", "response_code": None}

    @staticmethod
    def _sign_payload(secret, payload, timestamp):
        """Generate HMAC signature for webhook payload."""
        if isinstance(secret, bytes):
            secret_str = secret.decode("utf-8", errors="ignore")
        else:
            secret_str = str(secret)

        import json
        payload_str = json.dumps(payload, sort_keys=True) if isinstance(payload, dict) else str(payload)
        message = f"{timestamp}.{payload_str}"
        return hmac.new(
            secret_str.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def trigger_event(organization, event_type, payload):
        """Trigger webhooks for a given event type.

        Args:
            organization: Organization instance
            event_type: string event type (e.g., 'client.created')
            payload: dict payload to send
        """
        from apps.webhooks.models import WebhookEndpoint, WebhookDelivery

        endpoints = WebhookEndpoint.objects.filter(
            organization=organization,
            is_active=True,
        )
        if not endpoints.exists():
            return

        for endpoint in endpoints:
            if endpoint.events and event_type not in endpoint.events:
                continue
            WebhookDelivery.objects.create(
                endpoint=endpoint,
                event_type=event_type,
                payload=payload,
                status="pending",
            )
            # Trigger async delivery
            from apps.webhooks.tasks import deliver_webhook_task
            deliver_webhook_task.delay(endpoint.id)
