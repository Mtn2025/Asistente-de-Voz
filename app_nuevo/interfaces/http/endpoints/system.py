"""
System Endpoints.
"""
import logging

from fastapi import APIRouter, Depends

from app_nuevo.interfaces.http.dependencies import get_container, DIContainer

router = APIRouter(prefix="/system", tags=["System"])
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check(
    container: DIContainer = Depends(get_container)
):
    """Health Check."""
    # Check DB
    # We can try to resolve a repo and ping it
    status = {"status": "healthy", "database": "unknown"}
    
    try:
        from app_nuevo.domain.ports.config_repository_port import ConfigRepositoryPort
        repo = container.resolve(ConfigRepositoryPort)
        # Simple read to verify connection - use correct interface method
        config = await repo.get_config(profile="default")
        status["database"] = "connected"
    except Exception as e:
        logger.error(f"Health DB error: {e}")
        status["database"] = "disconnected"
        status["status"] = "unhealthy"
        
    return status
