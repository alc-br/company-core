import logging
import time
from apps.common.exceptions import AIProviderError, ServiceException
from apps.audit.services import AuditService

logger = logging.getLogger(__name__)


class AIService:
    """Central service for AI provider calls using Strategy Pattern."""

    @staticmethod
    async def call_ai(messages, model="gpt-4o", provider_name="openai", **kwargs):
        """Call an AI provider.

        Args:
            messages: list of message dicts [{"role": "user", "content": "..."}]
            model: model ID
            provider_name: 'openai', 'anthropic', 'gemini'
            **kwargs: additional params (temperature, max_tokens, etc.)

        Returns:
            dict with response, tokens, cost
        """
        import asyncio
        from apps.ai.models import AICallLog

        start_time = time.time()
        organization = kwargs.pop("organization", None)
        user = kwargs.pop("user", None)

        try:
            if provider_name == "openai":
                result = await AIService._call_openai(messages, model, **kwargs)
            elif provider_name == "anthropic":
                result = await AIService._call_anthropic(messages, model, **kwargs)
            elif provider_name == "gemini":
                result = await AIService._call_gemini(messages, model, **kwargs)
            else:
                raise AIProviderError(f"Unsupported provider: {provider_name}", provider=provider_name)

            latency_ms = int((time.time() - start_time) * 1000)
            tokens_input = result.get("tokens_input", 0)
            tokens_output = result.get("tokens_output", 0)

            # Log the call
            if organization:
                AICallLog.objects.create(
                    organization=organization,
                    user=user,
                    provider_name=provider_name,
                    model=model,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    cost=result.get("cost", 0),
                    latency_ms=latency_ms,
                )

            return result
        except AIProviderError:
            raise
        except Exception as e:
            logger.error(f"AI call failed: {provider_name}/{model}: {e}")
            raise AIProviderError(str(e), provider=provider_name)

    @staticmethod
    async def _call_openai(messages, model, **kwargs):
        """Call OpenAI API."""
        try:
            import openai
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs,
            )
            choice = response.choices[0]
            return {
                "content": choice.message.content,
                "tokens_input": response.usage.prompt_tokens if response.usage else 0,
                "tokens_output": response.usage.completion_tokens if response.usage else 0,
                "cost": 0,
                "raw_response": response.model_dump() if hasattr(response, "model_dump") else str(response),
            }
        except ImportError:
            raise AIProviderError("openai package not installed", provider="openai")
        except Exception as e:
            raise AIProviderError(str(e), provider="openai")

    @staticmethod
    async def _call_anthropic(messages, model, **kwargs):
        """Call Anthropic API."""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic()
            # Anthropic expects system separately
            system = kwargs.pop("system", None)
            response = await client.messages.create(
                model=model,
                messages=messages,
                system=system,
                **kwargs,
            )
            text = response.content[0].text if response.content else ""
            return {
                "content": text,
                "tokens_input": response.usage.input_tokens if response.usage else 0,
                "tokens_output": response.usage.output_tokens if response.usage else 0,
                "cost": 0,
                "raw_response": str(response),
            }
        except ImportError:
            raise AIProviderError("anthropic package not installed", provider="anthropic")
        except Exception as e:
            raise AIProviderError(str(e), provider="anthropic")

    @staticmethod
    async def _call_gemini(messages, model, **kwargs):
        """Call Google Gemini API."""
        try:
            import google.generativeai as genai
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            genai_model = genai.GenerativeModel(model)
            response = genai_model.generate_content(prompt)
            return {
                "content": response.text,
                "tokens_input": 0,
                "tokens_output": 0,
                "cost": 0,
                "raw_response": str(response),
            }
        except ImportError:
            raise AIProviderError("google-generativeai package not installed", provider="gemini")
        except Exception as e:
            raise AIProviderError(str(e), provider="gemini")
