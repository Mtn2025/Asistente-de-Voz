"""
Port (Interface) for Audio Transport.
Defines the contract for sending audio and control messages to clients.
"""
from abc import ABC, abstractmethod
from typing import Any

class AudioTransport(ABC):
    """
    Abstract interface for audio transport mechanisms (WebSocket, SIP, etc.).
    """
    
    @abstractmethod
    async def send_audio(self, audio_data: bytes, sample_rate: int = 8000) -> None:
        """
        Send audio data to the client.
        
        Args:
            audio_data: Raw audio bytes.
            sample_rate: Sample rate of the audio (default 8000Hz).
        """
        pass

    @abstractmethod
    async def send_json(self, data: dict[str, Any]) -> None:
        """
        Send a JSON control message to the client.
        
        Args:
            data: Dictionary to be serialized as JSON.
        """
        pass

    @abstractmethod
    def set_stream_id(self, stream_id: str) -> None:
        """
        Set the unique Stream/Call ID for this transport session.
        
        Args:
            stream_id: Unique identifier string.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the transport connection and release resources.
        """
        pass
