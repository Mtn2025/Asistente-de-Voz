"""
STT With Fallback Adapter.
"""
import logging
from collections.abc import Callable
from typing import Any

from app.domain.ports.stt_port import STTPort, STTRecognizer, STTConfig, STTException

logger = logging.getLogger(__name__)

class STTWithFallback(STTPort):
    """
    Wrapper for STT Port with Fallback logic.
    """

    def __init__(self, primary: STTPort, fallbacks: list[STTPort]):
        self.primary = primary
        self.fallbacks = fallbacks

    def create_recognizer(
        self,
        config: STTConfig,
        on_interruption_callback: Callable | None = None,
        event_loop: Any | None = None
    ) -> STTRecognizer:
        # For streaming, fallback is complex. 
        # Usually we just return primary recognizer. 
        # Ideally, we would return a wrapper that handles disconnects.
        # Check if legacy stt_with_fallback implemented logic.
        return self.primary.create_recognizer(config, on_interruption_callback, event_loop)

    async def transcribe_audio(self, audio_bytes: bytes, language: str = "es") -> str:
        try:
            return await self.primary.transcribe_audio(audio_bytes, language)
        except STTException as e:
            if not e.retryable or not self.fallbacks:
                raise

            logger.warning(f"Primary STT failed: {e}. Trying fallbacks...")
            
            for fb in self.fallbacks:
                try:
                    return await fb.transcribe_audio(audio_bytes, language)
                except Exception as ex:
                    logger.warning(f"Fallback STT failed: {ex}")
                    continue
            
            raise
    
    async def close(self):
        await self.primary.close()
        for fb in self.fallbacks:
            await fb.close()
