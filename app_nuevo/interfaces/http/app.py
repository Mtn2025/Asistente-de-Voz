"""
FastAPI Application Factory.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app_nuevo.infrastructure.config.settings import settings
from app_nuevo.infrastructure.di.container import DIContainer
from app_nuevo.infrastructure.di.registry import registry
from app_nuevo.interfaces.http.dependencies import get_container

# Routers
from app_nuevo.interfaces.http.endpoints import calls, config, history, system
from app_nuevo.interfaces.websocket import router as ws_router

# Middleware
from app_nuevo.interfaces.http.middleware.error_handler import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events for the application.
    """
    # Startup
    logger.info("🚀 Starting Voice Assistant App...")
    
    # Initialize DI Container
    # In dependencies.py we have a lazy loader, but we can force init here
    container = get_container()
    
    # Initialize Database
    from app_nuevo.infrastructure.database.session import init_db
    logger.info("🔧 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Voice Assistant App...")
    # Cleanup resources if needed
    # (e.g., container.close() or manage.disconnect())

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="Asistente de Voz AI",
        version="2.0.0",
        lifespan=lifespan
    )

    # --- Middleware ---
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Allow all for dev/legacy compatibility
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error Handler
    app.add_middleware(ErrorHandlerMiddleware)

    # --- Routers ---
    
    # HTTP
    app.include_router(calls.router, prefix="/api/calls") # Prefix convention? Legacy was mixed. 
    # Legacy: 
    # /twilio/incoming-call (in routes_telephony, mapped to /api? or root?)
    # /api/config
    # /api/history
    # /api/system
    
    # New Structure (Standardized under /api/v1 or similar, but keeping close to legacy paths for now)
    # Using specific prefixes as defined in routers or overrides here.
    # The routers themselves have prefixes defined in their files:
    # calls.py -> prefix="/calls" -> Total: /calls/... (Legacy was /twilio/...)
    # config.py -> prefix="/config" -> Total: /config/... (Legacy was /api/config)
    # history.py -> prefix="/history" -> Total: /history/... (Legacy was /api/history)
    # system.py -> prefix="/system" -> Total: /system/... (Legacy was /api/system)
    
    # We should mount them under /api to align with legacy /api/... structure mostly
    app.include_router(calls.router, prefix="/api") 
    app.include_router(config.router, prefix="/api")
    app.include_router(history.router, prefix="/api")
    app.include_router(system.router, prefix="/api")

    # WebSocket
    # WS Router has prefix="/simulator", so mounting it at root gives /simulator/stream
    # Legacy was /ws/simulator/stream? Or /api/v1/ws/media-stream?
    # Legacy routes_simulator: @router.websocket("/stream") -> mounted at?
    # Legacy routes_telephony: @router.websocket("/ws/media-stream")
    
    # Let's map WS to /ws for clarity
    app.include_router(ws_router.router, prefix="/ws") 

    return app
