class AISDK:
    @staticmethod
    async def complete(messages, model="gpt-4o", provider="openai", **kwargs):
        from apps.ai.services import AIService
        return await AIService.call_ai(messages, model=model, provider_name=provider, **kwargs)
