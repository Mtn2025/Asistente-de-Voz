"""
Port (Interface) for Tool Execution.
"""
from abc import ABC, abstractmethod
from typing import Any, Protocol

class ToolDefinition(Protocol):
    name: str
    description: str
    parameters: dict

class ToolPort(ABC):
    """
    Port for external tool integrations.
    """

    @abstractmethod
    async def execute(self, request: Any) -> Any:
        """
        Execute the tool with the provided request parameters.
        """
        pass

    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """
        Get the tool definition/schema for LLM function calling.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for the tool."""
        pass
