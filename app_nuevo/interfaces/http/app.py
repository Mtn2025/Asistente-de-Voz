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
from app_nuevo.domain.ports.config_repository_port import ConfigRepositoryPort

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
    from app_nuevo.infrastructure.database.seed import seed_default_config
    logger.info("🔧 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")
    
    # Seed default data
    logger.info("🌱 Seeding default data...")
    await seed_default_config()
    logger.info("✅ Seeding complete")
    
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

    # --- Static & Templates ---
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi import Request
    import json

    # Mount Static
    # Ensure directory exists, or this will raise error. We created it.
    app.mount("/static", StaticFiles(directory="app_nuevo/interfaces/http/static"), name="static")

    # Templates
    templates = Jinja2Templates(directory="app_nuevo/interfaces/http/templates")

    # --- Root Endpoint (Dashboard) ---
    @app.get("/", include_in_schema=False)
    async def root(request: Request):
        """
        Serve the Legacy Dashboard with injected configuration.
        """
        container = get_container()
        repo = container.resolve(ConfigRepositoryPort)

        # 1. Helper to fetch and map config
        async def get_profile_data(profile: str, suffix: str = ""):
            try:
                conf = await repo.get_config(profile=profile)
                # We need a mapper here similar to config.py but returning a simple dict
                # For now, we assume reasonable compatibility or use simple dict dump
                # The repo returns a Pydantic model usually, so model_dump is safe
                if hasattr(conf, 'model_dump'):
                    return conf.model_dump(), suffix
                return conf.__dict__, suffix
            except Exception as e:
                logger.error(f"Failed to load {profile} config: {e}")
                return {}, suffix

        # 2. Fetch all profiles
        browser_data, _ = await get_profile_data("browser")
        twilio_data, _ = await get_profile_data("twilio")
        telnyx_data, _ = await get_profile_data("telnyx")

        # 3. Merge into legacy "flat" structure
        # Legacy expects browser keys at root, and others with suffixes
        merged_config = {**browser_data} # Browser is base

        # Map Twilio keys with _phone suffix
        for k, v in twilio_data.items():
            merged_config[f"{k}_phone"] = v
            # Manual mapping for legacy impedance mismatches if needed
            if k == "llm_provider": merged_config["llm_provider_phone"] = v

        # Map Telnyx keys with _telnyx suffix
        for k, v in telnyx_data.items():
            merged_config[f"{k}_telnyx"] = v
            if k == "llm_provider": merged_config["llm_provider_telnyx"] = v

        # 4. Fetch Catalogs (Stubs for now, to be filled by Adapters)
        # In a real scenario, we'd resolve TTSAdapter/LLMAdapter here
        voices_json = {
            "azure": {
                "es-MX": [
                    {"id": "es-MX-DaliaNeural", "name": "Dalia (Femenino)", "gender": "female"},
                    {"id": "es-MX-JorgeNeural", "name": "Jorge (Masculino)", "gender": "male"}
                ],
                "en-US": [
                    {"id": "en-US-JennyNeural", "name": "Jenny (Female)", "gender": "female"}
                ]
            }
        }
        styles_json = {} # Azure styles
        models_json = {
            "groq": [{"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B"}],
            "openai": [{"id": "gpt-4o", "name": "GPT-4o"}]
        }
        langs_json = {
            "azure": [{"id": "es-MX", "name": "Español (México)"}, {"id": "en-US", "name": "Inglés (USA)"}]
        }

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "config_json": json.dumps(merged_config),
                "voices_json": json.dumps(voices_json),
                "styles_json": json.dumps(styles_json),
                "models_json": json.dumps(models_json),
                "langs_json": json.dumps(langs_json)
            }
        )

    return app
