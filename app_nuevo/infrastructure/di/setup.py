"""
DI Setup.

Configures dependencies and returns a ready-to-use Container.
"""
import logging
from typing import Any

from .registry import ComponentRegistry
from .container import DIContainer
from .providers import InfrastructureProviders, PersistenceProviders

# Ports
from ....domain.ports import (
    LLMPort,
    STTPort,
    TTSPort,
    CallRepositoryPort,
    ConfigRepositoryPort,
    TranscriptRepositoryPort,
    ExtractionPort
)

# Services
from ....application.services.voice_orchestrator import VoiceOrchestratorService
from ....application.services.pipeline_service import PipelineService

# Core Config
from app_nuevo.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

def configure_container() -> DIContainer:
    """
    Bootstraps the Dependency Injection Container.
    
    Returns:
        Configured DIContainer instance.
    """
    registry = ComponentRegistry()
    
    # --- Infrastructure Adapters (Singletons) ---
    
    # 1. LLM
    registry.register(
        LLMPort,
        implementation=lambda: InfrastructureProviders.provide_llm(settings),
        is_singleton=True
    )
    
    # 2. STT
    registry.register(
        STTPort,
        implementation=lambda: InfrastructureProviders.provide_stt(settings),
        is_singleton=True
    )
    
    # 3. TTS
    registry.register(
        TTSPort,
        implementation=lambda: InfrastructureProviders.provide_tts(settings),
        is_singleton=True
    )

    # 4. Extraction Logic
    registry.register(
        ExtractionPort,
        implementation=InfrastructureProviders.provide_extraction_service,
        is_singleton=True
    )
    
    # --- Persistence Adapters (Singletons/Factories) ---
    # Repositories manage their own session lifecycle via session_factory, so they can be Singletons.
    
    # 4. Call Repo
    registry.register(
        CallRepositoryPort,
        implementation=PersistenceProviders.provide_call_repository,
        is_singleton=True
    )
    
    # 5. Config Repo
    registry.register(
        ConfigRepositoryPort,
        implementation=PersistenceProviders.provide_config_repository,
        is_singleton=True
    )
    
    # 6. Transcript Repo (Optional)
    registry.register(
        TranscriptRepositoryPort,
        implementation=PersistenceProviders.provide_transcript_repository,
        is_singleton=True
    )
    
    # --- Application Services (Transient) ---
    
    # 7. Voice Orchestrator
    # Registered as a class. It has dependencies on Ports defined above.
    # It requires 'transport' to be passed at resolve time (overrides).
    registry.register(
        VoiceOrchestratorService,
        implementation=VoiceOrchestratorService,
        is_singleton=False 
    )
    
    # Note: PipelineService is created via PipelineFactory inside VoiceOrchestrator, 
    # so we don't necessarily need to register it here, but we could if we wanted to abstract the factory.
    
    logger.info("✅ DI Container configured successfully")
    return DIContainer(registry)


# Global Container Instance (Lazy loaded)
_container: DIContainer | None = None

def get_container() -> DIContainer:
    """Get or create the global container instance."""
    global _container
    if not _container:
        _container = configure_container()
    return _container
