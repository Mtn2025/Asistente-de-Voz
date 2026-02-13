"""
Global Error Handler Middleware.
"""
import logging
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch unhandled exceptions and return JSON responses.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled Exception: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "message": "Internal Server Error", "detail": str(e)}
            )
