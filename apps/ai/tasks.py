import logging
import asyncio
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_ai_call_task(self, provider_name, model, messages, **kwargs):
    """Process an AI call asynchronously (sync wrapper for async AIService)."""
    from apps.ai.services import AIService

    try:
        result = asyncio.run(AIService.call_ai(
            messages=messages,
            model=model,
            provider_name=provider_name,
            **kwargs,
        ))
        logger.info(f"AI call completed: {provider_name}/{model}")
        return {
            "content": result.get("content", "")[:500],
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
            "cost": str(result.get("cost", 0)),
        }
    except Exception as exc:
        logger.error(f"AI call failed ({provider_name}/{model}): {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def aggregate_ai_usage_task(self, organization_id, period_start, period_end):
    """Aggregate AI usage for billing."""
    from apps.ai.models import AICallLog
    from django.db.models import Sum, Count
    from datetime import datetime

    try:
        start = datetime.fromisoformat(period_start) if isinstance(period_start, str) else period_start
        end = datetime.fromisoformat(period_end) if isinstance(period_end, str) else period_end

        aggregation = AICallLog.objects.filter(
            organization_id=organization_id,
            created_at__gte=start,
            created_at__lte=end,
        ).aggregate(
            total_calls=Count("id"),
            total_tokens_input=Sum("tokens_input"),
            total_tokens_output=Sum("tokens_output"),
            total_cost=Sum("cost"),
            total_latency_ms=Sum("latency_ms"),
        )

        result = {
            "organization_id": organization_id,
            "period_start": str(start),
            "period_end": str(end),
            "total_calls": aggregation["total_calls"] or 0,
            "total_tokens_input": aggregation["total_tokens_input"] or 0,
            "total_tokens_output": aggregation["total_tokens_output"] or 0,
            "total_cost": str(aggregation["total_cost"] or 0),
            "avg_latency_ms": (
                (aggregation["total_latency_ms"] or 0) // (aggregation["total_calls"] or 1)
            ),
        }

        logger.info(
            f"AI usage aggregated for org {organization_id}: "
            f"{result['total_calls']} calls, "
            f"{result['total_tokens_input'] + result['total_tokens_output']} tokens"
        )
        return result
    except Exception as exc:
        logger.error(f"Failed to aggregate AI usage for org {organization_id}: {exc}")
        self.retry(exc=exc)
