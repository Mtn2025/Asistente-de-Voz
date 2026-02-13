"""
Application Layer DI Setup.
Registers Application Services on top of Infrastructure setup.
"""
from app_nuevo.infrastructure.di.setup import configure_infrastructure_container
from app_nuevo.infrastructure.di.container import DIContainer
from app_nuevo.application.services.voice_orchestrator import VoiceOrchestratorService
from app_nuevo.application.services.pipeline_service import PipelineService


def configure_application_container() -> DIContainer:
    """
    Extends infrastructure container with Application Services.
    
    Returns:
        DIContainer with both Infrastructure and Application components.
    """
    # Start with infrastructure container (ports/adapters)
    container = configure_infrastructure_container()
    registry = container._registry
    
    # Register Application Services
    registry.register(
        VoiceOrchestratorService,
        implementation=VoiceOrchestratorService,
        is_singleton=False
    )
    
    registry.register(
        PipelineService,
        implementation=PipelineService,
        is_singleton=False
    )
    
    return container
