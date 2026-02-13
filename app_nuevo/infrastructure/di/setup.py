"""
DI Setup.

Configures dependencies and returns a ready-to-use Container.
"""
import logging
from typing import Any

from app_nuevo.infrastructure.di.registry import ComponentRegistry
from app_nuevo.infrastructure.di.container import DIContainer
from app_nuevo.infrastructure.di.providers import InfrastructureProviders, PersistenceProviders

# Ports
from app_nuevo.domain.ports import (
    LLMPort,
    STTPort,
    TTSPort,
    CallRepositoryPort,
    ConfigRepositoryPort,
    TranscriptRepositoryPort,
    ExtractionPort
)

# Core Config
from app_nuevo.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

def configure_infrastructure_container() -> DIContainer:
    """
    Bootstraps Infrastructure Layer DI Container.
    Registers only Ports and their Adapter implementations.
    
    Returns:
        Configured DIContainer instance with Infrastructure components.
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
    
    logger.info("✅ Infrastructure DI Container configured successfully")
    return DIContainer(registry)


# Global Container Instance (Lazy loaded)
_container: DIContainer | None = None

def get_container() -> DIContainer:
    """Get or create the global container instance."""
    global _container
    if not _container:
        _container = configure_infrastructure_container()
    return _container
