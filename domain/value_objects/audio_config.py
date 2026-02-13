from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class AudioConfig:
    """
    Configuration object for audio format details.
    Decouples adapters from string-based 'client_type' or 'audio_mode'.
    """
    sample_rate: int
    encoding: Literal["pcm", "mulaw", "alaw"]
    channels: int
    bits_per_sample: int = 16

    @staticmethod
    def high_quality() -> "AudioConfig":
        """Configuration for High Fidelity usage (e.g. WebRTC/Browser)."""
        return AudioConfig(
            sample_rate=16000,
            encoding="pcm",
            channels=1,
            bits_per_sample=16
        )

    @staticmethod
    def telephony() -> "AudioConfig":
        """Configuration for Standard Telephony (8kHz mu-law)."""
        return AudioConfig(
            sample_rate=8000,
            encoding="mulaw", # Usually PCMU/8000
            channels=1,
            bits_per_sample=8
        )



    @staticmethod
    def from_legacy_mode(mode: str) -> "AudioConfig":
        """Helper to convert legacy string modes."""
        if mode == "browser":
            return AudioConfig.high_quality()
        else:
            # Default to Telephony for any other mode (inc. twilio/telnyx)
            return AudioConfig.telephony()
