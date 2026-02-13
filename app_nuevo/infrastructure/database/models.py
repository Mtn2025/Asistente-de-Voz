from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    func
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column

Base = declarative_base()

class AgentConfig(Base):
    """
    Configuration for the Voice Agent.
    Stored in DB to allow runtime updates via dashboard.
    """
    __tablename__ = "agent_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, default="default")
    
    # LLM
    llm_provider: Mapped[str] = mapped_column(String, default="groq")
    llm_model: Mapped[str] = mapped_column(String, default="llama-3.3-70b-versatile")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=150)
    system_prompt: Mapped[str] = mapped_column(Text, default="Eres un asistente útil.")
    first_message: Mapped[str] = mapped_column(Text, default="Hola, ¿en qué puedo ayudarte?")
    first_message_mode: Mapped[str] = mapped_column(String, default="standard")
    
    # TTS
    tts_provider: Mapped[str] = mapped_column(String, default="azure")
    voice_name: Mapped[str] = mapped_column(String, default="es-MX-DaliaNeural")
    voice_style: Mapped[str] = mapped_column(String, nullable=True)
    voice_speed: Mapped[float] = mapped_column(Float, default=1.0)
    voice_language: Mapped[str] = mapped_column(String, default="es-MX")
    
    # STT
    stt_provider: Mapped[str] = mapped_column(String, default="azure")
    stt_language: Mapped[str] = mapped_column(String, default="es-MX")
    
    # Advanced
    silence_timeout_ms: Mapped[int] = mapped_column(Integer, default=500)
    enable_denoising: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_backchannel: Mapped[bool] = mapped_column(Boolean, default=False)
    max_duration: Mapped[int] = mapped_column(Integer, default=300)
    
    # Provider Overlays
    silence_timeout_ms_phone: Mapped[int] = mapped_column(Integer, nullable=True)
    silence_timeout_ms_telnyx: Mapped[int] = mapped_column(Integer, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Call(Base):
    """
    Record of a voice call session.
    """
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stream_id: Mapped[str] = mapped_column(String, index=True) # session_id
    client_type: Mapped[str] = mapped_column(String)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")
    
    extraction_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    transcripts: Mapped[list["Transcript"]] = relationship("Transcript", back_populates="call", cascade="all, delete-orphan")


class Transcript(Base):
    """
    Transcript line from a call.
    """
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    call_id: Mapped[int] = mapped_column(Integer, ForeignKey("calls.id"))
    role: Mapped[str] = mapped_column(String) # user, assistant, system
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    call: Mapped["Call"] = relationship("Call", back_populates="transcripts")
