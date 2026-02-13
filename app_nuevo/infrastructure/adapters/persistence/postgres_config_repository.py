"""
Adaptador Postgres Config Repository - Implementación de ConfigRepositoryPort.

Wrappea el DBService existente y AgentConfig model manteniendo la
lógica de persistencia pero exponiendo un contrato hexagonal limpio.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app_nuevo.infrastructure.database.models import AgentConfig
from app_nuevo.domain.ports.config_repository_port import ConfigDTO, ConfigNotFoundException, ConfigRepositoryPort
from app_nuevo.infrastructure.database.db_service import db_service

logger = logging.getLogger(__name__)


class PostgresConfigRepository(ConfigRepositoryPort):
    """
    Repositorio para AgentConfig en PostgreSQL.

    Traduce entre el modelo SQLAlchemy (100+ columnas denormalizadas)
    y el ConfigDTO del dominio (campos esenciales).
    """

    def __init__(self, session_factory):
        """
        Args:
            session_factory: Callable returning async session context manager
        """
        self.session_factory = session_factory
        self._db_service = db_service

    async def get_config(self, profile: str = "default") -> ConfigDTO:
        """Obtiene configuración por perfil."""
        try:
            async with self.session_factory() as session:
                config_model = await self._db_service.get_agent_config(session)

                if not config_model:
                    raise ConfigNotFoundException(f"Config '{profile}' not found")

                # Map SQLAlchemy model to DTO
                return self._model_to_dto(config_model)

        except Exception as e:
            logger.error(f"❌ [Postgres Config Repo] Get failed: {e}")
            raise ConfigNotFoundException(str(e)) from e

    async def update_config(self, profile: str, **updates) -> ConfigDTO:
        """Actualiza configuración."""
        try:
            async with self.session_factory() as session:
                # Use existing db_service method
                await self._db_service.update_agent_config(session, **updates)

                # Fetch updated to disable detached instance issues
                # (Ideally db_service should return updated model or we re-fetch)
                updated_model = await self._db_service.get_agent_config(session)
                return self._model_to_dto(updated_model)

        except Exception as e:
            logger.error(f"❌ [Postgres Config Repo] Update failed: {e}")
            raise ConfigNotFoundException(str(e)) from e

    async def create_config(self, profile: str, config: ConfigDTO) -> ConfigDTO:
        """Crea nueva configuración."""
        try:
            async with self.session_factory() as session:
                # Convert DTO to model
                model = AgentConfig(name=profile)
                self._apply_dto_to_model(config, model)

                session.add(model)
                await session.commit()
                await session.refresh(model)

                return self._model_to_dto(model)

        except Exception as e:
            logger.error(f"❌ [Postgres Config Repo] Create failed: {e}")
            # Session rollback is handled by context manager usually or ignored if using standard patterns
            raise ConfigNotFoundException(str(e)) from e

    def _model_to_dto(self, model: AgentConfig) -> ConfigDTO:
        """Convierte AgentConfig model a ConfigDTO."""
        return ConfigDTO(
            # LLM
            llm_provider=model.llm_provider,
            llm_model=model.llm_model,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            system_prompt=model.system_prompt,
            first_message=model.first_message,
            first_message_mode=model.first_message_mode,
            # TTS
            tts_provider=model.tts_provider,
            voice_name=model.voice_name,
            voice_style=model.voice_style or "default",
            voice_speed=model.voice_speed,
            voice_language=model.voice_language or "es-MX",
            # STT
            stt_provider=model.stt_provider,
            stt_language=model.stt_language,
            silence_timeout_ms=model.silence_timeout_ms,
            # Advanced
            enable_denoising=model.enable_denoising,
            enable_backchannel=model.enable_backchannel,
            max_duration=model.max_duration,
            # Provider overlays
            silence_timeout_ms_phone=model.silence_timeout_ms_phone,
            silence_timeout_ms_telnyx=model.silence_timeout_ms_telnyx,
        )

    def _apply_dto_to_model(self, dto: ConfigDTO, model: AgentConfig):
        """Aplica valores del DTO al model."""
        model.llm_provider = dto.llm_provider
        model.llm_model = dto.llm_model
        model.temperature = dto.temperature
        model.max_tokens = dto.max_tokens
        model.system_prompt = dto.system_prompt
        model.first_message = dto.first_message
        model.first_message_mode = dto.first_message_mode
        model.tts_provider = dto.tts_provider
        model.voice_name = dto.voice_name
        model.voice_style = dto.voice_style
        model.voice_speed = dto.voice_speed
        model.voice_language = dto.voice_language
        model.stt_provider = dto.stt_provider
        model.stt_language = dto.stt_language
        model.silence_timeout_ms = dto.silence_timeout_ms
        model.enable_denoising = dto.enable_denoising
        model.enable_backchannel = dto.enable_backchannel
        model.max_duration = dto.max_duration
