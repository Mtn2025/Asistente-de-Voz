"""
Audio WebSocket Router.

Handles real-time audio streaming for Simulator/Browser.
"""
import asyncio
import contextlib
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from starlette.websockets import WebSocketState

from app_nuevo.interfaces.http.dependencies import get_container, DIContainer
from app_nuevo.interfaces.websocket.connection_manager import manager
from app_nuevo.application.services.voice_orchestrator import VoiceOrchestratorService
from app_nuevo.infrastructure.adapters.transport.simulator import SimulatorTransport
from app_nuevo.domain.value_objects.frames import TextFrame

# Ports required for Orchestrator Factory/Init
from app_nuevo.domain.ports import (
    STTPort, LLMPort, TTSPort, 
    ConfigRepositoryPort, CallRepositoryPort, TranscriptRepositoryPort
)

router = APIRouter(prefix="/simulator", tags=["Simulator"])
logger = logging.getLogger(__name__)

@router.websocket("/stream")
async def simulator_stream(
    websocket: WebSocket, 
    client_id: str | None = None,
    container: DIContainer = Depends(get_container)
):
    """
    Dedicated WebSocket for the Simulator/Browser.
    Path: /ws/simulator/stream
    """
    client_id = client_id or str(uuid.uuid4())
    logger.info(f"🖥️ Simulator Connected | ID: {client_id}")

    # 1. Accept & Register
    try:
        await manager.connect(client_id, websocket)
    except Exception as e:
        logger.error(f"Manager connect failed: {e}")
        return

    # 2. Setup Resources via DI
    try:
        # Resolve Ports
        # Note: In a real factory we'd have `OrchestratorFactory` to hide this complexity.
        # For now, we manually resolve ports to instantiate the service as per current architecture.
        stt = container.resolve(STTPort)
        llm = container.resolve(LLMPort)
        tts = container.resolve(TTSPort)
        config_repo = container.resolve(ConfigRepositoryPort)
        call_repo = container.resolve(CallRepositoryPort)
        transcript_repo = container.resolve(TranscriptRepositoryPort)
        
        # Tools (Optional)
        # tools = container.resolve(ToolsPort) or {} # If implemented
        tools = {} 

        # Transport Adapter
        transport = SimulatorTransport(websocket)

        # Instantiate Orchestrator
        orchestrator = VoiceOrchestratorService(
            transport=transport,
            stt_port=stt,
            llm_port=llm,
            tts_port=tts,
            config_repo=config_repo,
            call_repo=call_repo,
            transcript_repo=transcript_repo,
            client_type="browser",
            tools=tools
        )
        
        # Register for API control
        manager.register_orchestrator(client_id, orchestrator)
        
        # Start Service
        await orchestrator.start()

    except Exception as e:
        logger.error(f"Orchestrator setup failed: {e}")
        manager.disconnect(client_id, websocket)
        await websocket.close()
        return

    # 3. Main Loop
    try:
        while True:
            # Check connection state
            if websocket.client_state == WebSocketState.DISCONNECTED:
                break
                
            data = await websocket.receive_text()
            
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            # --- Event Handling ---
            event = msg.get("event")

            if event == "start":
                # Only if protocol requires explicit start signal acknowledgement
                pass
            
            elif event == "media":
                # Audio Payload
                payload = msg.get("media", {}).get("payload")
                if payload:
                    await orchestrator.process_audio(payload)
            
            elif event == "stop":
                logger.info(f"Stop signal received from {client_id}")
                break

            elif event == "text_input":
                # [Testing] Text Injection
                text = msg.get("text")
                if text and orchestrator.pipeline:
                    await orchestrator.pipeline.queue_frame(TextFrame(text=text))

            elif event == "client_interruption":
                 # [Interruption]
                 await orchestrator.handle_interruption(text="[User Interrupt]")
                 
    except WebSocketDisconnect:
        logger.info(f"Simulator disconnected: {client_id}")
        
    except Exception as e:
        logger.error(f"Simulator WS Error: {e}")
        
    finally:
        # 4. Cleanup
        manager.disconnect(client_id, websocket)
        if orchestrator:
            await orchestrator.stop()
        
        with contextlib.suppress(RuntimeError, Exception):
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
