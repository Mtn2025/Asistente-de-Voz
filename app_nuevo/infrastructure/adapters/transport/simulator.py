"""
Simulator Transport Adapter.

Adapts FastAPI WebSocket to AudioTransport Port.
"""
import base64
import contextlib
import json
import logging
from typing import Any

from fastapi import WebSocket

# Assuming Port Definition
from app_nuevo.domain.ports import AudioTransport

logger = logging.getLogger(__name__)

class SimulatorTransport(AudioTransport):
    """
    Adapter for the Browser Simulator using FastAPI WebSocket.
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.stream_id: str | None = None

    async def send_audio(self, audio_data: bytes, sample_rate: int = 8000) -> None:
        """
        Send audio chunk to browser simulator.
        Browser expects Base64 encoded audio in {"type": "audio", "data": "b64..."} JSON.
        """
        try:
            b64 = base64.b64encode(audio_data).decode("utf-8")
            # Log level debug to avoid spam
            # logger.debug(f"📤 [TRANS] Sending Audio: {len(b64)} chars")
            await self.websocket.send_text(json.dumps({
                "type": "audio", 
                "data": b64
            }))
        except Exception as e:
            logger.error(f"SimulatorTransport Send Error: {e}")
            # Don't raise, transport errors shouldn't crash pipeline logic if possible
            pass

    async def send_json(self, data: dict[str, Any]) -> None:
        """Send arbitrary JSON data."""
        with contextlib.suppress(Exception):
            await self.websocket.send_text(json.dumps(data))

    def set_stream_id(self, stream_id: str) -> None:
        """Set the stream ID (if needed for correlating logs/events)."""
        self.stream_id = stream_id

    async def close(self) -> None:
        """Close connection (if managed here)."""
        # Usually managed by the route handler
        with contextlib.suppress(Exception):
            await self.websocket.close()
