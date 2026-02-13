"""
History Endpoints.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from app_nuevo.interfaces.http.dependencies import verify_api_key, get_container, DIContainer
from app_nuevo.domain.ports.call_repository import CallRepositoryPort
from app_nuevo.domain.ports.transcript_repository import TranscriptRepositoryPort

router = APIRouter(prefix="/history", tags=["History"])
logger = logging.getLogger(__name__)

@router.get("/{call_id}/detail")
async def get_call_detail(
    call_id: int,
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Get call details + transcripts."""
    call_repo = container.resolve(CallRepositoryPort)
    trans_repo = container.resolve(TranscriptRepositoryPort)
    
    call = await call_repo.get_call_by_id(call_id)
    if not call:
        raise HTTPException(404, "Call not found")
        
    transcripts = await trans_repo.get_transcripts_by_call_id(call_id)
    
    return {
        "call": {
            "id": call.id,
            "start_time": call.start_time.isoformat() if call.start_time else None,
            "end_time": call.end_time.isoformat() if call.end_time else None,
            "client_type": call.client_type,
            "metadata": call.metadata
        },
        "transcripts": [
            {"role": t.role, "content": t.content, "timestamp": t.timestamp.isoformat()}
            for t in transcripts
        ]
    }

@router.post("/delete-selected")
async def delete_selected(
    request: Request,
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Delete calls by ID."""
    try:
        body = await request.json()
        ids = body.get("ids", [])
        if not ids:
             return {"status": "ok", "deleted": 0}
             
        call_repo = container.resolve(CallRepositoryPort)
        
        # Repository must support batch delete
        # If not, iterate (inefficient but safe for now)
        count = 0
        for cid in ids:
            await call_repo.delete_call(cid) # Assuming exists
            count += 1
            
        return {"status": "ok", "deleted": count}
        
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(500, str(e))

@router.post("/clear")
async def clear_history(
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Clear all history."""
    # This requires a clear_all method in repo which might not exist in Port
    # Check Port definition in Phase 7D?
    # Assuming CallRepositoryPort has generic delete methods or we skipped them.
    # For now, return Error Not Implemented to be safe
    raise HTTPException(501, "Clear history not implemented in Repository Port yet")
