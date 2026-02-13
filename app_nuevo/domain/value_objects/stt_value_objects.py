"""
STT Domain Value Objects.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any

class STTResultReason(Enum):
    """Razón del resultado STT."""
    RECOGNIZED_SPEECH = "recognized"
    RECOGNIZING_SPEECH = "recognizing"
    CANCELED = "canceled"
    UNKNOWN = "unknown"

@dataclass
class STTEvent:
    """Evento de reconocimiento STT."""
    reason: STTResultReason
    text: str
    duration: float = 0.0
    error_details: str | None = None

@dataclass
class STTConfig:
    """Configuración para reconocimiento STT (Base + Advanced)."""
    language: str = "es-MX"
    audio_mode: str = "twilio"  # "twilio", "telnyx", "browser"
    initial_silence_ms: int = 5000
    segmentation_silence_ms: int = 1000

    # Advanced Controls
    model: str = "default"
    keywords: list | None = None 
    silence_timeout: int = 500
    utterance_end_strategy: str = "default"

    # Formatting & Filters
    punctuation: bool = True
    profanity_filter: bool = True
    smart_formatting: bool = True

    # Features
    diarization: bool = False
    multilingual: bool = False
