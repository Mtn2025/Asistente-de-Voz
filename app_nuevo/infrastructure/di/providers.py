"""
DI Providers.

Factory functions for creating infrastructure adapters.
Isolates configuration logic from the Container.
"""
from typing import Any

# Ports
from app_nuevo.domain.ports import (
    LLMPort, STTPort, TTSPort, 
    CallRepositoryPort, ConfigRepositoryPort, TranscriptRepositoryPort, ExtractionPort
)

# Adapters
from app_nuevo.infrastructure.adapters.llm.groq_llm_adapter import GroqLLMAdapter
from app_nuevo.infrastructure.adapters.stt.azure_stt_adapter import AzureSTTAdapter
from app_nuevo.infrastructure.adapters.tts.azure_tts_adapter import AzureTTSAdapter
from app_nuevo.infrastructure.adapters.persistence.postgres_config_repository import PostgresConfigRepository
from app_nuevo.infrastructure.adapters.persistence.sqlalchemy_call_repository import SQLAlchemyCallRepository
from app_nuevo.infrastructure.adapters.persistence.sqlalchemy_transcript_repository import SQLAlchemyTranscriptRepository
from app_nuevo.infrastructure.adapters.extraction.groq_extraction_adapter import GroqExtractionAdapter

# DB
from app_nuevo.infrastructure.database.session import AsyncSessionLocal

class InfrastructureProviders:
    """
    Provides factory methods for Infrastructure components.
    """

    @staticmethod
    def provide_llm(config: Any = None) -> LLMPort:
        return GroqLLMAdapter(config)

    @staticmethod
    def provide_stt(config: Any = None) -> STTPort:
        return AzureSTTAdapter(config)

    @staticmethod
    def provide_tts(config: Any = None) -> TTSPort:
        return AzureTTSAdapter(config)

    @staticmethod
    def provide_extraction_service() -> ExtractionPort:
        return GroqExtractionAdapter()

    @staticmethod
    def provide_session_factory():
        return AsyncSessionLocal

    @staticmethod
    def provide_call_repository() -> CallRepositoryPort:
        # Returns a factory-based repository (creates sessions internally)
        return SQLAlchemyCallRepository(session_factory=AsyncSessionLocal)

    @staticmethod
    def provide_config_repository(session=None) -> ConfigRepositoryPort:
        # Note: ConfigRepository expects a specific session for atomic operations
        # or the caller manages the session. 
        # In our case, PostgresConfigRepository takes 'session'. 
        # For Singleton scope, this is tricky if session is short-lived.
        # BUT ConfigRepository is mostly used at startup (VoiceOrchestrator loads config).
        # We might need a wrapper that creates a fresh session for each call if injected as Singleton.
        
        # FIX: Since Orchestrator calls `await self._load_config()`, it uses `config_repo`.
        # PostgresConfigRepository needs a session. 
        # We will return a Factory that the container calls per request? 
        # Or we implement a "SessionAwareRepository".
        
        # For now, let's inject a scoped session proxy or just instantiate per use?
        # Actually, SQLAlchemyCallRepository handles its own sessions via factory.
        # PostgresConfigRepository takes `session`. We should refactor it to take `session_factory` 
        # to match CallRepository pattern for better DI compatibility.
        
        # WORKAROUND: For this phase, we'll assume runtime resolution or refactor later.
        pass

class PersistenceProviders:
    """
    Persistence Layer Providers.
    """
    
    @staticmethod
    def provide_call_repository() -> CallRepositoryPort:
        return SQLAlchemyCallRepository(session_factory=AsyncSessionLocal)
    
    @staticmethod
    def provide_transcript_repository() -> TranscriptRepositoryPort:
        return SQLAlchemyTranscriptRepository(session_factory=AsyncSessionLocal)

    @staticmethod
    def provide_config_repository() -> ConfigRepositoryPort:
        return PostgresConfigRepository(session_factory=AsyncSessionLocal)

