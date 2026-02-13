"""
Port (Interface) for Speech-to-Text (STT) providers.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Protocol

# We use Protocol for the Recognizer to avoid tight coupling if implementations vary wildly
class STTRecognizer(Protocol):
    """
    Interface for a streaming STT recognizer instance.
    """
    def subscribe(self, callback: Callable[[Any], None]) -> None: ...
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
        config: Any, # Typed as Any here to decouple from specific config DTOs for now
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
