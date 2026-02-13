"""
LLM Domain Value Objects.
"""
import json
from dataclasses import dataclass, field
from typing import Any

@dataclass
class LLMFunctionCall:
    """
    Function call emitted by LLM.
    """
    name: str
    arguments: dict[str, Any]
    call_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments,
            "call_id": self.call_id
        }

    @classmethod
    def from_openai_format(cls, tool_call: Any) -> "LLMFunctionCall":
        arguments = tool_call.function.arguments
        if isinstance(arguments, str):
            try:
                parsed_args = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_args = {}
        elif isinstance(arguments, dict):
             parsed_args = arguments
        else:
             parsed_args = {}

        return cls(
            name=tool_call.function.name,
            arguments=parsed_args,
            call_id=getattr(tool_call, 'id', None)
        )

@dataclass
class LLMChunk:
    """
    Single chunk from LLM streaming response.
    """
    text: str | None = None
    function_call: LLMFunctionCall | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_text(self) -> bool:
        return self.text is not None and len(self.text) > 0

    @property
    def has_function_call(self) -> bool:
        return self.function_call is not None

    @property
    def is_complete(self) -> bool:
        return self.finish_reason is not None

@dataclass
class ToolDefinitionForLLM:
    """
    Tool definition formatted for LLM function calling.
    """
    name: str
    description: str
    parameters: dict[str, Any]

    def to_openai_format(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

@dataclass
class LLMMessage:
    """
    Message in LLM conversation.
    """
    role: str
    content: str | None = None
    name: str | None = None
    function_call: LLMFunctionCall | None = None
    tool_calls: list[Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {"role": self.role}
        if self.content is not None:
             result["content"] = self.content
        if self.name:
             result["name"] = self.name
        if self.function_call:
             result["function_call"] = self.function_call.to_dict()
        if self.tool_calls:
             result["tool_calls"] = self.tool_calls
        return result
