from abc import ABC, abstractmethod
from typing import Any
import dataclasses

class ConfigNotFoundException(Exception):
    """Configuration profile not found."""
    pass

@dataclasses.dataclass
class ConfigDTO:
    """Data Transfer Object for Agent Configuration."""
    llm_provider: str | None = None
    llm_model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None
    first_message: str | None = None
    first_message_mode: str | None = None
    tts_provider: str | None = None
    voice_name: str | None = None
    voice_style: str | None = None
    voice_speed: float | None = None
    voice_language: str | None = None
    stt_provider: str | None = None
    stt_language: str | None = None
    silence_timeout_ms: int | None = None
    enable_denoising: bool | None = None
    enable_backchannel: bool | None = None
    max_duration: int | None = None
    silence_timeout_ms_phone: int | None = None
    silence_timeout_ms_telnyx: int | None = None

class ConfigRepositoryPort(ABC):
    """
    Port for accessing and managing application configuration.
    """

    @abstractmethod
    async def get_config(self, profile: str = "default") -> Any:
        pass

    @abstractmethod
    async def update_config(self, profile: str, **updates) -> Any:
        pass

    @abstractmethod
    async def create_config(self, profile: str, config: Any) -> Any:
        pass
