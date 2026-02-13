"""
Adaptador Groq LLM - Implementación de LLMPort.

Implementa lógica de streaming, validación de modelos y function calling
directamente sobre el cliente oficial de Groq.
"""

import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

import groq
from circuitbreaker import circuit
from groq import AsyncGroq

# Using legacy config for now until Infrastructure Config is fully migrated
from app_nuevo.infrastructure.config.settings import settings
# Decorators might be legacy, omitting for strict Hexagonal or should move them. 
# For now, we omit decorators if they are not critical, or we need to migrate them.
# The user wants "NO dependencias incorrectas". `app.core` is technically incorrect.
# I will comment out the decorator usage if I cannot access it, or import if valid.
# `app.core.decorators` is internal. 
# Decided: Comment out decorator and add TODO to migrate observability.

from app_nuevo.domain.value_objects.llm_value_objects import LLMChunk, LLMFunctionCall
from app_nuevo.domain.ports.llm_port import LLMException, LLMPort, LLMRequest

logger = logging.getLogger(__name__)

# Model Safety Constants
SAFE_MODELS_FOR_VOICE = [
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-specdec",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-4-maverick-17b-128e",
    "gemma-2-9b-it",
    "gemma-7b",
    "mixtral-8x7b-32768"
]

REASONING_MODELS = [
    "deepseek-r1-distill-llama-70b",
    "deepseek-chat",
    "deepseek-reasoner"
]

class GroqLLMAdapter(LLMPort):
    """
    Adaptador para Groq LLM que implementa LLMPort.
    """

    def __init__(self, config: Any | None = None):
        api_key = config.api_key if config else settings.GROQ_API_KEY
        self.default_model = config.model if config else settings.GROQ_MODEL

        if not api_key:
             logger.warning("⚠️ Groq API Key missing. Adapter may fail.")

        self.client = AsyncGroq(api_key=api_key)

    @circuit(failure_threshold=3, recovery_timeout=60, expected_exception=LLMException)
    # @track_streaming_latency("groq_llm") # TODO: Migrate Observability
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        trace_id = request.metadata.get('trace_id', 'unknown') if request.metadata else 'unknown'
        start_time = time.time()
        first_byte_time = None

        try:
            logger.info(f"[LLM Groq] trace={trace_id} Starting generation model={request.model}")

            if request.model in REASONING_MODELS:
                logger.warning(
                    f"⚠️ REASONING MODEL ALERT: '{request.model}' generates <think> tags!"
                )

            # Map LLMMessage objects to dicts
            # Assuming request.messages is a list of LLMMessage objects (migrated) or dicts
            messages_dict = []
            for msg in request.messages:
                if hasattr(msg, 'role'):
                     messages_dict.append({"role": msg.role, "content": msg.content})
                else:
                     messages_dict.append(msg)

            system_prompt = request.system_prompt or "Eres un asistente útil."
            if system_prompt:
                messages_dict.insert(0, {"role": "system", "content": system_prompt})

            api_params = {
                "model": request.model or self.default_model or "llama-3.3-70b-versatile",
                "messages": messages_dict,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": True,
                "stop": ["User:", "System:", "\n\nUser", "\n\nSystem"]
            }

            if request.tools:
                # Map ToolDefinition to dicts
                tools_dicts = []
                for tool in request.tools:
                    if hasattr(tool, 'to_openai_format'):
                        tools_dicts.append(tool.to_openai_format())
                    else:
                        tools_dicts.append(tool)
                        
                api_params["tools"] = tools_dicts
                api_params["tool_choice"] = "auto"

            stream = await self.client.chat.completions.create(**api_params)

            function_call_buffer = {
                "name": "",
                "arguments": "",
                "id": None
            }
            in_function_call = False

            async for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason

                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    tool_call = delta.tool_calls[0]
                    in_function_call = True

                    if tool_call.id:
                        function_call_buffer["id"] = tool_call.id
                    if hasattr(tool_call, 'function') and tool_call.function:
                        if tool_call.function.name:
                            function_call_buffer["name"] += tool_call.function.name
                        if tool_call.function.arguments:
                            function_call_buffer["arguments"] += tool_call.function.arguments

                    if first_byte_time is None:
                        first_byte_time = time.time()
                        ttfb = (first_byte_time - start_time) * 1000
                        logger.info(f"[LLM Groq] trace={trace_id} TTFB={ttfb:.0f}ms (function_call)")

                elif delta.content:
                    token = delta.content

                    if first_byte_time is None:
                        first_byte_time = time.time()
                        ttfb = (first_byte_time - start_time) * 1000
                        logger.info(f"[LLM Groq] trace={trace_id} TTFB={ttfb:.0f}ms")

                    yield LLMChunk(text=token)

                if finish_reason:
                    if in_function_call and function_call_buffer["name"]:
                        try:
                            arguments = json.loads(function_call_buffer["arguments"])
                            function_call = LLMFunctionCall(
                                name=function_call_buffer["name"],
                                arguments=arguments,
                                call_id=function_call_buffer["id"]
                            )

                            logger.info(f"[LLM Groq] Function call: {function_call.name}")

                            yield LLMChunk(
                                function_call=function_call,
                                finish_reason=finish_reason
                            )
                        except json.JSONDecodeError:
                            yield LLMChunk(
                                text="[Error: Failed to parse function call]",
                                finish_reason=finish_reason
                            )
                    else:
                        yield LLMChunk(finish_reason=finish_reason)

        except Exception as e:
            logger.error(f"[Groq] Error: {e}")
            raise LLMException(f"Groq Error: {e}", retryable=True, provider="groq", original_error=e)

    async def get_available_models(self) -> list[str]:
        try:
            models = await self.client.models.list()
            return [m.id for m in models.data if "whisper" not in m.id]
        except Exception:
            return SAFE_MODELS_FOR_VOICE[:4]

    def is_model_safe_for_voice(self, model: str) -> bool:
        return model not in REASONING_MODELS
