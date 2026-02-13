"""
Use Case: Synthesize Text
Encapsulates Text-to-Speech synthesis logic.
"""
import logging
from dataclasses import dataclass
from typing import Any

from app_nuevo.domain.ports.tts_port import TTSPort, TTSRequest
# Assuming VoiceConfig is available (Value Object)
from app_nuevo.domain.value_objects.voice_config import VoiceConfig 

logger = logging.getLogger(__name__)

@dataclass
class SynthesizeTextRequest:
    text: str
    voice_config: VoiceConfig

@dataclass
class SynthesizeTextResponse:
    audio_data: bytes
    format: str = "wav"

class SynthesizeTextUseCase:
    """
    Orchestrates TTS synthesis.
    """

    def __init__(self, tts_port: TTSPort):
        self.tts = tts_port

    async def execute(self, request: SynthesizeTextRequest) -> SynthesizeTextResponse:
        if not request.text or not request.text.strip():
            return SynthesizeTextResponse(audio_data=b"")

        # Domain Logic: SSML building would go here or in VO
        # For strict port usage:
        
        tts_request = TTSRequest(
            text=request.text,
            voice_id=request.voice_config.name,
            speed=request.voice_config.speed,
            # map other config fields
        )
        
        # If Port supports raw text, great. If it needs SSML, use builder.
        # Assuming Port handles this abstraction via Request DTO
        
        audio_bytes = await self.tts.synthesize(tts_request)
        return SynthesizeTextResponse(audio_data=audio_bytes)
