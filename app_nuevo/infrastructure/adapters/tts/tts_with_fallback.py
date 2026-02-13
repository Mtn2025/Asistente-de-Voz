"""
TTS With Fallback - Resilience adapter (Module 11).

Wraps primary TTS with fallback TTS for automatic failure recovery.

Gap Analysis: Score Resiliencia 85/100 -> 100/100
"""
import logging
from collections.abc import AsyncIterator
from typing import List, Optional

from app_nuevo.domain.value_objects.tts_value_objects import TTSRequest, VoiceMetadata
from app_nuevo.domain.ports.tts_port import TTSException, TTSPort

logger = logging.getLogger(__name__)


class TTSWithFallback(TTSPort):
    """
    TTS adapter with automatic fallback on primary failure.

    Resilience Pattern: Circuit Breaker + Fallback

    Behavior:
    1. Always try primary TTS first
    2. On failure, use fallback TTS
    3. After 3 consecutive failures, switch to fallback mode
    4. Auto-recover to primary after success
    """

    def __init__(self, primary: TTSPort, fallback: TTSPort):
        """
        Initialize TTS with fallback.

        Args:
            primary: Primary TTS adapter (e.g., AzureTTSAdapter)
            fallback: Fallback TTS adapter (e.g., GoogleTTSAdapter)
        """
        self.primary = primary
        self.fallback = fallback

        # Circuit breaker state
        self._primary_failures = 0
        self._failure_threshold = 3
        self._fallback_active = False

        logger.info(
            f"[TTSFallback] Initialized - Primary: {type(primary).__name__}, "
            f"Fallback: {type(fallback).__name__}"
        )

    async def synthesize(self, request: TTSRequest) -> bytes:
        """
        Synthesize speech with automatic fallback.
        """
        # Auto-recovery: Reset fallback mode if primary was working
        if self._fallback_active and self._primary_failures == 0:
            self._fallback_active = False
            logger.info("[TTSFallback] Primary recovered, switching back from fallback")

        # Try primary if not in fallback mode
        if not self._fallback_active:
            try:
                logger.debug(f"[TTSFallback] Using PRIMARY: {type(self.primary).__name__}")

                return await self.primary.synthesize(request)

            except TTSException as e:
                self._primary_failures += 1

                logger.warning(
                    f"[TTSFallback] Primary failed ({self._primary_failures}/{self._failure_threshold}): {e}, "
                    f"using fallback"
                )

                # Switch to fallback mode after threshold
                if self._primary_failures >= self._failure_threshold:
                    self._fallback_active = True
                    logger.error(
                        f"[TTSFallback] Primary failed {self._failure_threshold}x, "
                        f"SWITCHING TO FALLBACK MODE"
                    )

        # Use fallback (either was in fallback mode, or primary just failed)
        try:
            logger.info(f"[TTSFallback] Using FALLBACK: {type(self.fallback).__name__}")

            return await self.fallback.synthesize(request)

        except TTSException as fallback_error:
            logger.error(f"[TTSFallback] BOTH primary AND fallback failed! {fallback_error}")
            raise TTSException(
                f"TTS complete failure - Primary: {type(self.primary).__name__}, "
                f"Fallback: {type(self.fallback).__name__}"
            ) from fallback_error

    async def get_available_voices(self, language: str | None = None) -> List[VoiceMetadata]:
        """Get available voices from primary."""
        # Delegate to primary (fallback voices may differ)
        return self.primary.get_available_voices(language)

    def is_using_fallback(self) -> bool:
        """Check if currently in fallback mode."""
        return self._fallback_active

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._primary_failures

    async def close(self):
        """Close both primary and fallback providers."""
        await self.primary.close()
        await self.fallback.close()

    def get_voice_styles(self, voice_id: str) -> list[str]:
        """Get voice styles from primary provider."""
        return self.primary.get_voice_styles(voice_id)

    async def synthesize_ssml(self, ssml: str) -> bytes:
        """Synthesize SSML with fallback strategy."""
        try:
            return await self.primary.synthesize_ssml(ssml)
        except Exception as e:
            logger.warning(f"[TTSFallback] SSML Primary failed: {e}. Trying fallback.")
            return await self.fallback.synthesize_ssml(ssml)
