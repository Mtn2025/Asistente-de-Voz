"""
TTS Domain Value Objects.
"""
from dataclasses import dataclass

@dataclass
class VoiceMetadata:
    """Metadata de una voz disponible."""
    id: str
    name: str
    gender: str
    locale: str

@dataclass
class TTSRequest:
    """
    Voice synthesis request (Domain Model).
    """
    text: str
    voice_id: str
    language: str = "es-MX"

    # Generic parameters
    pitch: int = 0
    speed: float = 1.0
    volume: float = 100.0
    format: str = "pcm_16000"
    style: str = None
    backpressure_detected: bool = False

    # Provider-specific options
    provider_options: dict = None

    # Metadata
    metadata: dict = None

    def __post_init__(self):
        """Initialize default dicts if None."""
        if self.provider_options is None:
            self.provider_options = {}
        if self.metadata is None:
            self.metadata = {}
