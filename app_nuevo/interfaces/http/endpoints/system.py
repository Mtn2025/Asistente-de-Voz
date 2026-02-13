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
    Run onnxruntime diagnostic script internally and return output.
    This is a temporary endpoint for debugging.
    """
    import subprocess
    import os
    
    script_path = "/app/diagnose_onnx.sh"
    
    if not os.path.exists(script_path):
        return {"error": f"Script not found at {script_path}"}
        
    try:
        # Ensure executable
        subprocess.run(["chmod", "+x", script_path], check=False)
        
        # Run script
        result = subprocess.run(
            ["/bin/bash", script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "system_info": {
                "platform": os.uname().sysname,
                "machine": os.uname().machine,
                "release": os.uname().release
            }
        }
    except Exception as e:
        logger.error(f"Diagnostic failed: {e}")
        return {"error": str(e)}
