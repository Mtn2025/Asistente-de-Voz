"""
Use Case: Handle Barge-In
Encapsulates logic for user interruption.
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HandleBargeInRequest:
    reason: str
    # Future extensibility: call_id, audio_frame, etc.

@dataclass
class HandleBargeInResponse:
    clear_pipeline: bool
    interrupt_audio: bool
    reason: str

class HandleBargeInUseCase:
    """
    Determines actions to take when an interruption (Barge-In) occurs.
    """

    async def execute(self, request: HandleBargeInRequest) -> HandleBargeInResponse:
        logger.info(f"[HandleBargeIn] Analyzing interruption: {request.reason}")

        # Domain Logic
        is_user_speech = "user" in request.reason.lower() or "vad" in request.reason.lower()
        
        if is_user_speech:
            return HandleBargeInResponse(
                clear_pipeline=True,
                interrupt_audio=True,
                reason=request.reason
            )
            
        return HandleBargeInResponse(
            clear_pipeline=False,
            interrupt_audio=True,
            reason=request.reason
        )
