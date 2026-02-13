"""
Use Case: Process Incoming Audio
Validates and prepares user audio input for processing.
"""
import logging
import base64
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class ProcessAudioRequest:
    payload: str  # Base64 string
    client_type: str
    stream_id: str

@dataclass
class ProcessAudioResponse:
    audio_bytes: Optional[bytes]
    sample_rate: int
    is_valid: bool
    error: str | None = None

class ProcessAudioUseCase:
    """
    Domain logic for handling incoming audio:
    - Decodes Base64
    - Validates content
    - Determines sample rate based on client
    """

    def execute(self, request: ProcessAudioRequest) -> ProcessAudioResponse:
        # 1. Decode
        try:
            audio_bytes = base64.b64decode(request.payload)
            if not audio_bytes:
                return ProcessAudioResponse(None, 0, False, "Empty audio payload")
        except Exception as e:
            return ProcessAudioResponse(None, 0, False, f"Decoding failed: {e}")

        # 2. Determine Sample Rate
        # Domain rule: Browser = 16k, Telephony = 8k
        sample_rate = 16000 if request.client_type == "browser" else 8000

        # 3. Success
        return ProcessAudioResponse(
            audio_bytes=audio_bytes,
            sample_rate=sample_rate,
            is_valid=True
        )
