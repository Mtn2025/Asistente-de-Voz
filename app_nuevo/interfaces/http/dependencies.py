"""
HTTP Dependencies.

Shared dependencies for HTTP endpoints (Authentication, DI, etc.).
"""
import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader

from app_nuevo.infrastructure.di.container import DIContainer
# Import the properly configured container from infrastructure setup
from app_nuevo.infrastructure.di.setup import get_container
from app_nuevo.infrastructure.config.settings import settings

# --- Authentication ---

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    api_key: str = Security(API_KEY_HEADER)
) -> str:
    """
    Verify API Key from header.
    """
    if not settings.API_KEY:
        # If no key configured, allow all (Review security policy)
        return "dev-mode"

    if api_key == settings.API_KEY:
        return api_key
    
    # Check Admin/Service keys if applicable
    # (Legacy logic was simple comparison)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

async def require_twilio_signature(request: Request):
    """
    Validate Twilio Request Signature.
    (Stub for migration - Legacy used 'require_twilio_signature')
    """
    # TODO: Migrate full signature validation from app_nuevo.core.webhook_security
    # For now, pass to avoid breaking if not strictly enforced in dev
    return True

async def require_telnyx_signature(request: Request):
    """
    Validate Telnyx Request Signature.
    (Stub for migration)
    """
    return True

# Type alias for Container
ContainerDep = Annotated[DIContainer, Depends(get_container)]

