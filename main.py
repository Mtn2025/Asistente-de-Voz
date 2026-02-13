"""
Main Entry Point - Asistente de Voz (App Nuevo).
"""
import uvicorn
from app_nuevo.interfaces.http.app import create_app

# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    import os

    # Read port from environment (Coolify/Traefik compatibility)
    port = int(os.getenv("PORT", "8000"))

    # Dev Server Configuration
    uvicorn.run(
        "app_nuevo.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,      # Hot reload for development
        log_level="info"
    )
