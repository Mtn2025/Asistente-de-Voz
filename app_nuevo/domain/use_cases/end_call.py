"""
Use Case: End Call
Orchestrates the finalization and cleanup of a voice call session.
"""
import logging
from dataclasses import dataclass
from typing import Any, List, Dict

from app_nuevo.domain.ports.call_repository_port import CallRepositoryPort
from app_nuevo.domain.ports.extraction_port import ExtractionPort
from app_nuevo.domain.ports.transcript_repository_port import TranscriptRepositoryPort

logger = logging.getLogger(__name__)

@dataclass
class EndCallRequest:
    call_id: int
    stream_id: str
    conversation_history: List[Dict[str, str]]

@dataclass
class EndCallResponse:
    success: bool
    extracted_data: Any | None = None

class EndCallUseCase:
    """
    Orchestrates call finalization:
    1. Triggers Post-Call Analysis (Extraction)
    2. Updates Call Record with extraction data
    3. Marks Call as Ended in Repository
    """

    def __init__(
        self,
        call_repo: CallRepositoryPort,
        extraction_port: ExtractionPort,
        transcript_repo: TranscriptRepositoryPort | None = None
    ):
        self.call_repo = call_repo
        self.extraction_port = extraction_port
        self.transcript_repo = transcript_repo

    async def execute(self, request: EndCallRequest) -> EndCallResponse:
        logger.info(f"🏁 [EndCallUseCase] Ending call {request.call_id}")
        
        extracted_data = None

        # 1. Post-Call Analysis
        if request.conversation_history:
            try:
                logger.info("🔎 [EndCallUseCase] Requesting post-call extraction...")
                extracted_data = await self.extraction_port.extract_post_call(
                    stream_id=request.stream_id,
                    conversation_history=request.conversation_history
                )
                
                if extracted_data:
                     await self.call_repo.update_call_extraction(request.call_id, extracted_data)
                     logger.info("✅ [EndCallUseCase] Extraction saved")

            except Exception as e:
                logger.error(f"⚠️ [EndCallUseCase] Extraction failed: {e}")
                # Non-blocking failure

        # 2. Finalize Call
        try:
            await self.call_repo.end_call(request.call_id)
            logger.info("✅ [EndCallUseCase] Call closed in DB")
            return EndCallResponse(success=True, extracted_data=extracted_data)
        except Exception as e:
             logger.error(f"❌ [EndCallUseCase] Failed to close call: {e}")
             return EndCallResponse(success=False, extracted_data=extracted_data)
