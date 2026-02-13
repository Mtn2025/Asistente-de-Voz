"""
Port (Interface) for Speech-to-Text (STT) providers.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

class STTException(Exception):
    """Base exception for STT errors."""
    pass

@dataclass
class STTConfig:
    """
    Configuration for STT recognition.
    """
    language: str = "es-ES"
    sample_rate: int = 16000
    channels: int = 1
    enable_denoising: bool = False

@dataclass
class STTEvent:
    """
    Event emitted by STT recognizer.
    """
    text: str
    is_final: bool
    confidence: float = 1.0
    speech_detected: bool = True

# We use Protocol for the Recognizer to avoid tight coupling if implementations vary wildly
class STTRecognizer(Protocol):
    """
    Interface for a streaming STT recognizer instance.
    """
    def subscribe(self, callback: Callable[[STTEvent | Any], None]) -> None: ...
    async def start_continuous_recognition(self) -> None: ...
    async def stop_continuous_recognition(self) -> None: ...
    def write(self, audio_data: bytes) -> None: ...


class STTPort(ABC):
    """
    Port defining operations for Speech-to-Text services.
    """

    @abstractmethod
    def create_recognizer(
        self,
        config: STTConfig | Any,
        on_interruption_callback: Callable | None = None,
        event_loop: Any | None = None
    ) -> STTRecognizer:
        """
        Create a configured STT recognizer instance for streaming.
        """
        pass

    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes, language: str = "es") -> str:
        """
        Transcribe a complete audio chunk (non-streaming).
        
        Args:
            audio_bytes: Raw audio data.
            language: Language code (default 'es').
            
        Returns:
            Transcribed text.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Release provider resources."""
        pass
