"""
Database seeding utilities.

Provides functions to seed initial data into the database.
"""
import logging
from sqlalchemy import select

from app_nuevo.infrastructure.database.models import AgentConfig
from app_nuevo.infrastructure.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def seed_default_config():
    """Seed default agent config if not exists."""
    async with AsyncSessionLocal() as session:
        try:
            # Check if default config exists
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.name == "default")
            )
            existing = result.scalars().first()
            
            if existing:
                logger.info("✅ Default config already exists")
                return
            
            # Create default config with sensible defaults
            default_config = AgentConfig(
                name="default",
                # LLM
                llm_provider="groq",
                llm_model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=150,
                system_prompt="Eres un asistente útil.",
                first_message="Hola, ¿en qué puedo ayudarte?",
                first_message_mode="standard",
                # TTS
                tts_provider="azure",
                voice_name="es-MX-DaliaNeural",
                voice_style=None,
                voice_speed=1.0,
                voice_language="es-MX",
                # STT
                stt_provider="azure",
                stt_language="es-MX",
                # Advanced
                silence_timeout_ms=500,
                enable_denoising=True,
                enable_backchannel=False,
                max_duration=300,
            )
            
            session.add(default_config)
            await session.commit()
            
            logger.info("✅ Default config created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error seeding default config: {e}")
            await session.rollback()
            raise
