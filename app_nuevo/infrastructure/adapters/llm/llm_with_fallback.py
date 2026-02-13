"""
Fallback Wrapper for LLM Port.
"""
import logging
from collections.abc import AsyncIterator

from app_nuevo.domain.ports.llm_port import LLMException, LLMPort, LLMRequest, LLMChunk

logger = logging.getLogger(__name__)

class LLMWithFallback(LLMPort):
    """
    LLM Port wrapper with graceful degradation.
    """

    def __init__(self, primary: LLMPort, fallbacks: list[LLMPort]):
        self.primary = primary
        self.fallbacks = fallbacks

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        try:
            logger.info("[LLM Fallback] Attempting primary provider")
            async for chunk in self.primary.generate_stream(request):
                yield chunk
            return

        except LLMException as e:
            if not e.retryable or not self.fallbacks:
                raise

            logger.warning(f"[LLM Fallback] Primary failed: {e}. Trying fallbacks...")

        for i, fallback in enumerate(self.fallbacks):
            try:
                logger.info(f"[LLM Fallback] Fallback {i+1}")
                async for chunk in fallback.generate_stream(request):
                    yield chunk
                return

            except LLMException:
                if i == len(self.fallbacks) - 1:
                    raise
                continue

    async def get_available_models(self) -> list[str]:
        return await self.primary.get_available_models()

    def is_model_safe_for_voice(self, model: str) -> bool:
        return self.primary.is_model_safe_for_voice(model)
