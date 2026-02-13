"""
Port (Interface) for Text-to-Speech (TTS) providers.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from dataclasses import dataclass

@dataclass
class VoiceMetadata:
    """Metadata for an available voice."""
    id: str
    name: str
    gender: str
    locale: str

class TTSPort(ABC):
    """
    Port defining operations for Text-to-Speech services.
    """

    @abstractmethod
    async def synthesize(self, request: Any) -> bytes:
        """
        Synthesize text to audio.
        
        Args:
             request: TTS synthesis request parameters.
             
        Returns:
             Raw audio bytes.
        """
        pass

    @abstractmethod
    async def synthesize_ssml(self, ssml: str) -> bytes:
        """
        Synthesize audio directly from SSML markup.
        """
        pass

    @abstractmethod
    def get_available_voices(self, language: Optional[str] = None) -> List[VoiceMetadata]:
        """
        Get list of available voices, optionally filtered by language.
        """
        pass

    @abstractmethod
    def get_voice_styles(self, voice_id: str) -> List[str]:
        """
        Get supported emotional/speaking styles for a specific voice.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Release provider resources."""
        pass
