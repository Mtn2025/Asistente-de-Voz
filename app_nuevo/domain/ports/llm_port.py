"""
Port (Interface) for Large Language Models (LLM).
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, List, Protocol

from app_nuevo.domain.value_objects.llm_value_objects import LLMChunk, LLMFunctionCall, LLMMessage

class LLMException(Exception):
    """Exception for LLM errors."""
    def __init__(self, message: str, retryable: bool = False, provider: str = "unknown", original_error: Exception | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.provider = provider
        self.original_error = original_error

@dataclass
class LLMRequest:
    """
    Standard request for LLM generation.
    """
    messages: List[LLMMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int = 150
    system_prompt: str = ""
    tools: List[Any] | None = None
    metadata: dict = None

class LLMPort(ABC):
    """
    Port defining operations for LLM providers.
    """

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        """
        Generate a streaming response from the LLM.
        """
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """
        Get a list of model identifiers available from the provider.
        """
        pass

    @abstractmethod
    def is_model_safe_for_voice(self, model: str) -> bool:
        """
        Check if a specific model is considered safe/suitable for voice interactions.
        """
        pass
