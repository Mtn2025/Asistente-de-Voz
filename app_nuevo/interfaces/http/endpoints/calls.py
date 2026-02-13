"""
Calls Endpoints.
Handles Telephony Webhooks and Test Calls.
"""
import base64
import json
import logging
import time
import uuid
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app_nuevo.infrastructure.config.settings import settings
from app_nuevo.interfaces.http.dependencies import (
    verify_api_key,
    get_container,
    DIContainer,
    require_twilio_signature,
    require_telnyx_signature
)

# [Legacy] State tracking
active_calls: Dict[str, Dict[str, Any]] = {}

router = APIRouter(prefix="/calls", tags=["Calls"])
logger = logging.getLogger(__name__)

# --- Twilio ---

@router.api_route("/twilio/incoming-call", methods=["GET", "POST"])
async def incoming_call_twilio(
    request: Request,
    container: DIContainer = Depends(get_container)
    # signature: bool = Depends(require_twilio_signature)
):
    """
    Twilio incoming call webhook.
    Returns TwiML to connect to WebSocket.
    """
    host = request.headers.get("host")
    # Clean TwiML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{host}/api/v1/ws/media-stream" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


# --- Telnyx ---

@router.post("/telnyx/call-control")
async def telnyx_call_control(
    request: Request,
    container: DIContainer = Depends(get_container)
    # signature: bool = Depends(require_telnyx_signature)
):
    """
    Telnyx Call Control Webhook.
    Handles 'call.initiated', 'call.answered' events.
    """
    try:
        body = await request.json()
        data = body.get("data", {})
        event_type = data.get("event_type")
        payload = data.get("payload", {})
        call_control_id = payload.get("call_control_id")

        logger.info(f"📞 [Telnyx] Event: {event_type} | ID: {call_control_id}")

        if event_type == "call.initiated":
            active_calls[call_control_id] = {
                "state": "initiated",
                "initiated_at": time.time()
            }
            # Execute Answer Logic
            await _answer_call_telnyx(call_control_id)

        elif event_type == "call.answered":
            logger.info(f"📱 [Telnyx] Answered: {call_control_id}")
            client_state = payload.get("client_state")
            
            # Start Streaming
            await _start_streaming_telnyx(call_control_id, request, client_state)
            
            # Start Noise Suppression
            await _start_suppression_telnyx(call_control_id)

        return {"status": "received", "event_type": event_type}

    except Exception as e:
        logger.error(f"❌ Telnyx Webhook Error: {e}")
        return {"status": "error", "message": str(e)}


# --- Test Calls ---

@router.post("/test/telnyx")
async def test_call_telnyx(
    request: Request,
    _ = Depends(verify_api_key),
    container: DIContainer = Depends(get_container)
):
    """Initiate a test outbound call via Telnyx."""
    try:
        body = await request.json()
        target_number = body.get("to")
        if not target_number:
            raise HTTPException(status_code=400, detail="Missing 'to' phone number")

        # Resolve Config via Repository (Clean Arch)
        from app_nuevo.domain.ports.config_repository_port import ConfigRepositoryPort
        config_repo = container.resolve(ConfigRepositoryPort)
        # Assuming agent_id 1 for test
        config = await config_repo.get_agent_config(1)
        
        if not config:
             raise HTTPException(status_code=404, detail="Config not found")

        # Get Telnyx Profile
        # Note: Depending on Config entity implementation, might need to access attributes logic
        # For now assume flattened or dynamic props access
        telnyx_api_key = getattr(config, 'telnyx_api_key', None) or settings.TELNYX_API_KEY
        # Fallback logic for props
        source_number = getattr(config, 'caller_id_telnyx', None) or \
                        getattr(config, 'telnyx_from_number', None)
        connection_id = getattr(config, 'telnyx_connection_id', None)

        if not all([telnyx_api_key, source_number, connection_id]):
             raise HTTPException(status_code=400, detail="Missing Telnyx Configuration (Key, Number, or ID)")

        # Execute Outbound Call
        url = f"{settings.TELNYX_API_BASE}/calls"
        headers = {
            "Authorization": f"Bearer {telnyx_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": target_number,
            "from": source_number,
            "connection_id": connection_id
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "status": "success", 
                "call_id": data.get("data", {}).get("call_control_id")
            }
        
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test Call Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/twilio")
async def test_call_twilio(
    request: Request,
    _ = Depends(verify_api_key)
):
    """Initiate Twilio Test Call."""
    # Stub for now
    return {"status": "success", "message": "Twilio test call initiated (stub)"}


# --- Internal Helpers (To be moved to Infrastructure Service) ---

async def _answer_call_telnyx(call_id: str):
    """Helper to answer Telnyx call."""
    api_key = settings.TELNYX_API_KEY
    url = f"{settings.TELNYX_API_BASE}/calls/{call_id}/actions/answer"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Encode state
    state_json = json.dumps({"call_control_id": call_id})
    client_state = base64.b64encode(state_json.encode()).decode()
    
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json={"client_state": client_state})


async def _start_streaming_telnyx(call_id: str, request: Request, client_state: str | None):
    """Helper to start media streaming."""
    host = request.headers.get("host")
    scheme = request.headers.get("x-forwarded-proto", "https")
    ws_scheme = "wss" if scheme == "https" else "ws"
    
    # Safe encoding
    from urllib.parse import quote
    encoded_id = quote(call_id, safe='')
    
    ws_url = f"{ws_scheme}://{host}/api/v1/ws/media-stream?client=telnyx&call_control_id={encoded_id}"
    if client_state:
        ws_url += f"&client_state={client_state}"

    url = f"{settings.TELNYX_API_BASE}/calls/{call_id}/actions/streaming_start"
    api_key = settings.TELNYX_API_KEY
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {
        "stream_url": ws_url,
        "stream_track": "inbound_track",
        "stream_bidirectional_mode": "rtp",
        "stream_bidirectional_codec": "PCMA"
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)

async def _start_suppression_telnyx(call_id: str):
    """Helper for noise suppression."""
    url = f"{settings.TELNYX_API_BASE}/calls/{call_id}/actions/suppression_start"
    api_key = settings.TELNYX_API_KEY
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json={"direction": "both"})
