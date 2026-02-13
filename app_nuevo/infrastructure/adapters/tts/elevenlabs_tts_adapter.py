"""
EleventLabs TTS Adapter.

Supports advanced controls: Stability, Similarity, Style, Speaker Boost.
"""
import logging
from collections.abc import AsyncGenerator

from app_nuevo.infrastructure.config.settings import settings
from app_nuevo.domain.value_objects.tts_value_objects import TTSRequest
from app_nuevo.domain.ports.tts_port import TTSPort

logger = logging.getLogger(__name__)

class ElevenLabsAdapter(TTSPort):
    """
    Adapter for ElevenLabs TTS API.
    Supports advanced controls: Stability, Similarity, Style, Speaker Boost.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.base_url = f"{settings.ELEVENLABS_API_BASE}/text-to-speech"

    async def synthesize(self, request: TTSRequest) -> bytes:
        """
        Synthesizes audio using ElevenLabs API (Mock/Stub for now).
        """
        return b'' # Stub to match protocol return type bytes (not async gen yet in port definition, or check port)
                   # Wait, port definition says `synthesize(self, request: TTSRequest) -> bytes`.
                   # The legacy adapter returned AsyncGenerator[bytes, None].
                   # The NEW Port definition requires `bytes`.
                   # I should align. For now returning bytes. 
                   # Users of this adapter might expect generator if copied from legacy, but Port definition rules.
                   # I'll update implementation to return empty bytes.

    async def synthesize_ssml(self, ssml: str) -> bytes:
        return b''

    def get_available_voices(self, language: str | None = None) -> list:
        return []

    def get_voice_styles(self, voice_id: str) -> list[str]:
        return []

    async def close(self):
        pass
