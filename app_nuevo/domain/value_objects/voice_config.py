"""Value Objects for Voice Configuration (Type-Safe)."""
from dataclasses import dataclass
from typing import Literal, Dict, Any

# Type aliases
AudioMode = Literal["browser", "twilio", "telnyx"]
VoiceStyle = Literal["default", "cheerful", "sad", "angry", "friendly", "terrified", "excited", "hopeful"]
AudioEncoding = Literal["pcm", "mulaw", "alaw"]

@dataclass(frozen=True)
class VoiceConfig:
    """
    Immutable voice configuration value object.
    
    Attributes:
        name: Azure voice name
        speed: Speech rate multiplier (0.5 - 2.0)
        pitch: Pitch offset in Hz (-100 to +100)
        volume: Volume level (0-100)
        style: Speaking style
        style_degree: Style intensity (0.01 - 2.0)
    """
    name: str
    speed: float = 1.0
    pitch: int = 0
    volume: int = 100
    style: VoiceStyle = "default"
    style_degree: float = 1.0

    def __post_init__(self):
        """Validate field values."""
        if not (0.5 <= self.speed <= 2.0):
            raise ValueError(f"Speed must be between 0.5 and 2.0, got {self.speed}")

        if not (-100 <= self.pitch <= 100):
            raise ValueError(f"Pitch must be between -100 and +100 Hz, got {self.pitch}")

        if not (0 <= self.volume <= 100):
            raise ValueError(f"Volume must be between 0 and 100, got {self.volume}")

        if not (0.01 <= self.style_degree <= 2.0):
            raise ValueError(f"Style degree must be between 0.01 and 2.0, got {self.style_degree}")

    def to_ssml_params(self) -> Dict[str, Any]:
        """Convert to SSML builder parameters."""
        return {
            "voice_name": self.name,
            "rate": self.speed,
            "pitch": self.pitch,
            "volume": self.volume,
            "style": self.style if self.style != "default" else None,
            "style_degree": self.style_degree if self.style != "default" else None
        }


@dataclass(frozen=True)
class AudioFormat:
    """
    Audio format specification (immutable).
    """
    sample_rate: int
    channels: int = 1
    bits_per_sample: int = 16
    encoding: AudioEncoding = "mulaw"

    @property
    def is_telephony(self) -> bool:
        return self.sample_rate == 8000 and self.encoding in ["mulaw", "alaw"]

    @property
    def is_browser(self) -> bool:
        return self.sample_rate == 16000 and self.encoding == "pcm"

    @classmethod
    def for_client_type(cls, client_type: str) -> 'AudioFormat':
        """Factory method to create AudioFormat based on client type."""
        if client_type == "browser":
            return cls(sample_rate=16000, encoding="pcm")
        if client_type in ["twilio", "telnyx"]:
            return cls(sample_rate=8000, encoding="mulaw")
        return cls(sample_rate=8000, encoding="mulaw")
