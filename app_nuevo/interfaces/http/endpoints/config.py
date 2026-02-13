"""
Configuration Endpoints.
Handles Profile Management and Dynamic Options.
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from app_nuevo.interfaces.http.dependencies import verify_api_key, get_container, DIContainer
from app_nuevo.domain.ports.config_repository_port import ConfigRepositoryPort

# Schemas
from app_nuevo.interfaces.schemas.browser_schemas import BrowserConfigUpdate
from app_nuevo.interfaces.schemas.twilio_schemas import TwilioConfigUpdate
from app_nuevo.interfaces.schemas.telnyx_schemas import TelnyxConfigUpdate
from app_nuevo.interfaces.schemas.config_schemas import CoreConfigUpdate

router = APIRouter(prefix="/config", tags=["Configuration"])
logger = logging.getLogger(__name__)

# [NOTE] Field Aliases should ideally be in a Mapper, using dict for now to match legacy behavior
FIELD_ALIASES = {
    # ... (Copied from legacy for compatibility)
    'provider': 'llm_provider', 'model': 'llm_model', 'temp': 'temperature',
    'tokens': 'max_tokens', 'prompt': 'system_prompt', 'msg': 'first_message',
    'voiceProvider': 'tts_provider', 'voiceId': 'voice_name', 'voiceStyle': 'voice_style',
    'voiceSpeed': 'voice_speed', 'sttProvider': 'stt_provider', 'sttLang': 'stt_language',
    'interruptWords': 'interruption_threshold', 'silence': 'silence_timeout_ms',
    # ... (Add full list from legacy if strictly required for frontend, simplified for brevity)
    # The schemas themselves have 'alias' defined, so Pydantic handles input.
    # This dict is mainly for OUTPUT mapping (DB -> Frontend).
}

# Helper for OUTPUT mapping
def _map_db_to_frontend(config_obj: Any, profile: str) -> Dict[str, Any]:
    """Map DB Entity/Model to Frontend Dict using Aliases."""
    # This logic replicates endpoints logic from legacy
    # TODO: Extract to Mapper Class
    result = {}
    
    # Determine Schema
    if profile == "browser":
        schema = BrowserConfigUpdate
    elif profile == "twilio":
        schema = TwilioConfigUpdate
    elif profile == "telnyx":
        schema = TelnyxConfigUpdate
    else:
        return {}

    # Map fields
    for field_name, field_info in schema.model_fields.items():
        frontend_key = field_info.alias or field_name
        # DB attribute (snake_case)
        db_attr = field_name 
        val = getattr(config_obj, db_attr, None)
        if val is not None:
            result[frontend_key] = val
            
    return result


@router.get("/")
async def get_config(
    profile: str = "browser",
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Get configuration for a profile."""
    repo = container.resolve(ConfigRepositoryPort)
    try:
        config = await repo.get_config(profile=profile)
    except Exception as e:
        logger.error(f"Config get error: {e}")
        raise HTTPException(status_code=404, detail="Config not found")
        
    try:
        data = _map_db_to_frontend(config, profile)
        return data
    except Exception as e:
        logger.error(f"Config map error: {e}")
        raise HTTPException(status_code=500, detail="Mapping error")


# --- Updates ---

async def _update_config_generic(container: DIContainer, profile: str, data: dict):
    """Generic update helper."""
    repo = container.resolve(ConfigRepositoryPort)
    
    # Update config using Port interface
    try:
        await repo.update_config(profile=profile, **data)
        return True
    except Exception as e:
        logger.error(f"Config update error: {e}")
        raise HTTPException(500, f"Update failed: {e}")


@router.patch("/browser")
async def update_browser(
    bg_config: BrowserConfigUpdate,
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Update Browser Profile."""
    await _update_config_generic(container, "browser", bg_config.model_dump(exclude_unset=True))
    return {"status": "ok", "message": "Browser config updated"}

@router.patch("/twilio")
async def update_twilio(
    tw_config: TwilioConfigUpdate,
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Update Twilio Profile."""
    await _update_config_generic(container, "twilio", tw_config.model_dump(exclude_unset=True))
    return {"status": "ok", "message": "Twilio config updated"}

@router.patch("/telnyx")
async def update_telnyx(
    tx_config: TelnyxConfigUpdate,
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Update Telnyx Profile."""
    await _update_config_generic(container, "telnyx", tx_config.model_dump(exclude_unset=True))
    return {"status": "ok", "message": "Telnyx config updated"}


@router.post("/patch")
async def patch_config_generic(
    request: Request,
    container: DIContainer = Depends(get_container),
    _ = Depends(verify_api_key)
):
    """Generic Patch (JSON)."""
    body = await request.json()
    repo = container.resolve(ConfigRepositoryPort)
    
    # Determine profile from body or default
    profile = body.pop("profile", "default")
    
    try:
        await repo.update_config(profile=profile, **body)
        return {"status": "ok", "updated": list(body.keys())}
    except Exception as e:
        logger.error(f"Config patch error: {e}")
        raise HTTPException(500, f"Update failed: {e}")


# --- Dynamic Options ---
# (Requires adapters, normally cached)

@router.get("/options/tts/languages")
async def get_languages(_ = Depends(verify_api_key)):
    # Helper or Adapter call
    # For Phase 11B, stub or direct simple return
    return {"languages": ["es-MX", "en-US"]} # Stub to unblock

@router.get("/options/tts/voices")
async def get_voices(language: str | None = None, _ = Depends(verify_api_key)):
    # Stub
    return {"voices": []}

@router.get("/options/tts/styles")
async def get_styles(voice_id: str, _ = Depends(verify_api_key)):
    # Stub
    return {"styles": []}
