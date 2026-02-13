"""
System Endpoints.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from app_nuevo.interfaces.http.dependencies import get_container, DIContainer, verify_api_key
from app_nuevo.domain.ports.config_repository_port import ConfigRepositoryPort

router = APIRouter(prefix="/system", tags=["System"])
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check(container: DIContainer = Depends(get_container)):
    """
    Health check endpoint.
    Checks database connection and returns system status.
    """
    try:
        # Check Database
        repo = container.resolve(ConfigRepositoryPort)
        # We just need to check if DB is reachable, get_config is a safe read
        await repo.get_config(profile="default")
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"System unhealthy: {str(e)}"
        )

@router.get("/diagnostic/onnx")
async def diagnostic_onnx(
    _ = Depends(verify_api_key)
):
    """
    Run onnxruntime diagnostic (Pure Python version).
    Checks architecture and imports without blocking subprocesses.
    """
    import sys
    import platform
    import importlib.util
    
    info = {
        "platform": sys.platform,
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "onnxruntime_installed": False,
        "onnxruntime_version": None,
        "import_error": None
    }
    
    # Check if package is installed
    spec = importlib.util.find_spec("onnxruntime")
    if spec:
        info["onnxruntime_installed"] = True
        try:
            import onnxruntime
            info["onnxruntime_version"] = onnxruntime.__version__
            info["status"] = "SUCCESS"
        except ImportError as e:
            info["import_error"] = str(e)
            info["status"] = "IMPORT_FAILED"
        except Exception as e:
            info["import_error"] = f"Unexpected error: {str(e)}"
            info["status"] = "ERROR"
    else:
        info["status"] = "NOT_INSTALLED"
        
    return info
