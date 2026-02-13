"""
Configuration Schemas for Core/Global
"""

from pydantic import BaseModel, Field


class CoreConfigUpdate(BaseModel):
    """
    Core/Global configuration.
    """
    stt_provider: str | None = Field(None, max_length=50, alias="sttProvider")
    llm_provider: str | None = Field(None, max_length=50, alias="llmProvider")
    tts_provider: str | None = Field(None, max_length=50, alias="voiceProvider")
    extraction_model: str | None = Field(None, max_length=100, alias="extractionModel")

    model_config = {"extra": "ignore", "populate_by_name": True}
