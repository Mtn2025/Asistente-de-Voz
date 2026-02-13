"""
Tool Domain Value Objects.
"""
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class ToolDefinition:
    """
    Metadata definition for a tool exposed to LLM.
    """
    name: str
    description: str
    parameters: dict[str, Any]
    required: list[str] = field(default_factory=list)

    def to_openai_format(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required
                }
            }
        }

@dataclass
class ToolRequest:
    """
    Request to execute a tool.
    """
    tool_name: str
    arguments: dict[str, Any]
    trace_id: str
    timeout_seconds: float = 10.0

@dataclass
class ToolResponse:
    """
    Result of tool execution.
    """
    tool_name: str
    result: Any
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    trace_id: str = "unknown"
