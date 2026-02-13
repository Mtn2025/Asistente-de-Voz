"""
Use Case: Execute Tool
Encapsulates logic for executing external tools.
"""
import logging
from dataclasses import dataclass
from typing import Dict, Any

from app_nuevo.domain.ports.tool_port import ToolPort, ToolDefinition

logger = logging.getLogger(__name__)

@dataclass
class ToolExecutionRequest:
    tool_name: str
    arguments: Dict[str, Any]
    trace_id: str

@dataclass
class ToolExecutionResponse:
    success: bool
    result: Any
    error: str | None = None

class ExecuteToolUseCase:
    """
    Orchestrates execution of registered tools.
    """

    def __init__(self, tools: Dict[str, ToolPort]):
        self.tools = tools

    async def execute(self, request: ToolExecutionRequest) -> ToolExecutionResponse:
        tool = self.tools.get(request.tool_name)
        
        if not tool:
            return ToolExecutionResponse(
                success=False, 
                result=None, 
                error=f"Tool {request.tool_name} not found"
            )

        try:
            # ToolPort.execute expects its own Request object, typically
            # But here we adapt. Assuming Port follows protocol.
            # Using Any for flexibility as ToolPort definition earlier used specific models
            
            # NOTE: In a real migration, we match the DTOs exactly.
            # Here we assume the Port's execute takes a compatible object or dict.
            result = await tool.execute(request) 
            
            # Start adapting result
            return ToolExecutionResponse(
                success=getattr(result, 'success', True),
                result=getattr(result, 'result', result),
                error=getattr(result, 'error_message', None)
            )
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolExecutionResponse(success=False, result=None, error=str(e))

    def get_definitions(self) -> list[ToolDefinition]:
        return [t.get_definition() for t in self.tools.values()]
