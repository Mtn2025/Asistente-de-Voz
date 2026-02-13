"""
Use Case: Start Call
Orchestrates the initialization of a voice call session.
"""
import logging
from dataclasses import dataclass
from typing import Optional, Any

from app_nuevo.domain.entities.call import Call, CallStatus
from app_nuevo.domain.value_objects.call_id import CallId
from app_nuevo.domain.value_objects.call_context import CallMetadata
from app_nuevo.domain.ports.call_repository_port import CallRepositoryPort
from app_nuevo.domain.ports.config_repository_port import ConfigRepositoryPort

logger = logging.getLogger(__name__)

@dataclass
class StartCallRequest:
    stream_id: str
    client_type: str
    metadata: dict[str, Any]
    agent_id: int = 1

@dataclass
class StartCallResponse:
    call: Call
    config: Any # AgentConfig from repository
    is_new: bool

class StartCallUseCase:
    """
    Orchestrates call initialization:
    1. Loads Agent Configuration
    2. Creates/Persists Call Record
    3. Returns Call Entity and Config for orchestrator
    """

    def __init__(
        self,
        call_repo: CallRepositoryPort,
        config_repo: ConfigRepositoryPort
    ):
        self.call_repo = call_repo
        self.config_repo = config_repo

    async def execute(self, request: StartCallRequest) -> StartCallResponse:
        logger.info(f"🚀 [StartCallUseCase] Starting call {request.stream_id} (Agent {request.agent_id})")

        # 1. Load Configuration
        try:
            config = await self.config_repo.get_config(str(request.agent_id))
            if not config:
                raise ValueError(f"Config not found for agent {request.agent_id}")
        except Exception as e:
            logger.error(f"❌ [StartCallUseCase] Config load failed: {e}")
            raise

        # 2. Create Call Record (Persistence)
        # Note: Port currently returns CallRecord (DTO), we map to Entity
        # In a purer implementation, Port would return Entity directly.
        try:
            call_record_dto = await self.call_repo.create_call(
                stream_id=request.stream_id,
                client_type=request.client_type,
                metadata=request.metadata
            )
            
            # Map DTO to Entity
            call = Call(
                id=CallId(str(call_record_dto.id)), # Assuming DB ID maps to CallId
                metadata=CallMetadata(
                   session_id=request.stream_id,
                   client_type=request.client_type,
                   phone_number=request.metadata.get('from', None)
                ),
                status=CallStatus.ACTIVE,
                started_at=call_record_dto.started_at
            )
            
            logger.info(f"✅ [StartCallUseCase] Call initialized: {call.id}")
            
            return StartCallResponse(
                call=call,
                config=config,
                is_new=True
            )

        except Exception as e:
            logger.error(f"❌ [StartCallUseCase] Call creation failed: {e}")
            raise
