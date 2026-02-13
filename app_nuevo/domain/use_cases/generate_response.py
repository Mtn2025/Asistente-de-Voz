"""
Use Case: Generate Response
Encapsulates LLM interaction and conversation management.
"""
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, List

from app_nuevo.domain.ports.llm_port import LLMPort, LLMRequest, LLMMessage
# Note: PromptBuilder might need to be migrated to a Domain Service or Port
# For now, we assume it exists or we mock it.
from app_nuevo.application.components.prompt_builder import PromptBuilder 

logger = logging.getLogger(__name__)

@dataclass
class GenerateResponseRequest:
    user_message: str
    conversation_history: List[dict] # {role, content}
    config: Any # AgentConfig
    context: dict | None = None

class GenerateResponseUseCase:
    """
    Orchestrates response generation:
    1. Updates History
    2. Builds System Prompt
    3. Streams response from LLM Port
    """

    def __init__(self, llm_port: LLMPort):
        self.llm = llm_port

    async def execute(self, request: GenerateResponseRequest) -> AsyncGenerator[str, None]:
        # 1. Validate Input
        if not request.user_message or not request.user_message.strip():
            logger.warning("Job skipped: Empty user message")
            return

        # 2. Update History (In-Memory Reference)
        # Avoid duplicates check (Domain Logic)
        if not request.conversation_history or request.conversation_history[-1].get("content") != request.user_message:
             request.conversation_history.append({"role": "user", "content": request.user_message})

        # 3. Build Prompt (Domain Service call would be better here)
        try:
            # Using existing PromptBuilder (to be refactored later)
            system_prompt = PromptBuilder.build_system_prompt(request.config, request.context or {})
        except Exception:
            system_prompt = getattr(request.config, 'system_prompt', "You are a helpful assistant.")

        # 4. Stream Response
        llm_request = LLMRequest(
            messages=[LLMMessage(role=m['role'], content=m['content']) for m in request.conversation_history],
            model=getattr(request.config, 'llm_model', 'default'),
            temperature=getattr(request.config, 'temperature', 0.7),
            max_tokens=getattr(request.config, 'max_tokens', 150),
            system_prompt=system_prompt
        )

        full_response = ""
        async for chunk in self.llm.generate_stream(llm_request):
             # chunk might be complex, simplified here assuming string yield from port wrapper
             # If Port yields objects, we extract text
             text_chunk = chunk.text if hasattr(chunk, 'text') else str(chunk)
             full_response += text_chunk
             yield text_chunk

        # 5. Append Assistant Response
        if full_response.strip():
            request.conversation_history.append({"role": "assistant", "content": full_response})
