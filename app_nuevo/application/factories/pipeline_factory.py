"""
Pipeline Factory - Encapsulates pipeline construction logic.
Decouples the Orchestrator from concrete processor instantiation.
"""
import asyncio
import logging
from collections.abc import Callable
from typing import Any

# Managers & Utils (Legacy imports allowed temporarily for Managers/Processors)
from app_nuevo.infrastructure.messaging.control_channel import ControlChannel
from app_nuevo.infrastructure.services.crm_service import CRMService
from app_nuevo.application.components.hold_audio import HoldAudioPlayer

# New Services
from app_nuevo.application.services.pipeline_service import PipelineService, FrameProcessor
from app_nuevo.application.common.frame_processor import FrameDirection

# Ports (New)
from app_nuevo.domain.ports import LLMPort, STTPort, TTSPort

# Domain Logic (Use Cases)
# Domain Logic (Use Cases)
from app_nuevo.domain.use_cases import DetectTurnEndUseCase, ExecuteToolUseCase

# Processors (Application Components)
from app_nuevo.application.components.context_aggregator import ContextAggregator
from app_nuevo.application.components.llm_processor import LLMProcessor
from app_nuevo.application.components.metrics_processor import MetricsProcessor
from app_nuevo.application.components.transcript_reporter import TranscriptReporter
from app_nuevo.application.components.stt_processor import STTProcessor
from app_nuevo.application.components.tts_processor import TTSProcessor
from app_nuevo.application.components.vad_processor import VADProcessor
from app_nuevo.application.components.output_sink import PipelineOutputSink

logger = logging.getLogger(__name__)

class PipelineFactory:
    """
    Factory for creating configured Voice Pipelines.
    """

    @staticmethod
    async def create_pipeline(
        config: Any,
        stt_port: STTPort,
        llm_port: LLMPort,
        tts_port: TTSPort,
        control_channel: ControlChannel,
        conversation_history: list[dict[str, str]],
        initial_context_data: dict[str, Any],
        crm_service: CRMService | None,
        tools: dict[str, Any],
        stream_id: str,
        transcript_callback: Callable[[str, str], Any],
        orchestrator_ref: Any,  # Interface compliant with PipelineOutputSink expectation
        loop: asyncio.AbstractEventLoop
    ) -> PipelineService:
        """
        Builds and initializes the processing pipeline.

        Args:
            config: AgentConfig model
            stt_port: STT Provider
            llm_port: LLM Provider
            tts_port: TTS Provider
            control_channel: Signal channel (Legacy)
            conversation_history: Shared history list
            initial_context_data: Call context
            crm_manager: CRM Manager (optional)
            tools: Tool definitions
            stream_id: Unique trace ID
            transcript_callback: Callback for reporter events
            orchestrator_ref: Reference to orchestrator (for sink)
            loop: Asyncio loop

        Returns:
            PipelineService: Initialized pipeline instance
        """

        # 1. STT Processor
        # Injects control channel for out-of-band signaling
        stt = STTProcessor(
            provider=stt_port,
            config=config,
            loop=loop,
            control_channel=control_channel
        )
        await stt.initialize()

        # 2. VAD Processor
        # Injects strict domain use case for turn detection
        detect_turn_end = DetectTurnEndUseCase(
            silence_threshold_ms=getattr(config, 'silence_timeout_ms', 500)
        )
        vad = VADProcessor(
            config=config,
            detect_turn_end=detect_turn_end,
            control_channel=control_channel
        )

        # 3. Context Aggregator
        agg = ContextAggregator(
            config=config,
            conversation_history=conversation_history,
            llm_provider=llm_port,  # Needed for semantic context analysis
            transcript_callback=transcript_callback # [FEEDBACK] Direct Reporting
        )

        # 4. LLM Processor
        # Prepare context data (CRM + Initial)
        context_data = initial_context_data.copy()
        if crm_service and crm_service.crm_context:
            context_data['crm'] = crm_service.crm_context

        # Tool Use Case
        execute_tool_use_case = ExecuteToolUseCase(tools)

        # Hold Audio Player (for tool execution delays)
        # Assuming orchestrator_ref has audio_manager (migrated or legacy)
        hold_audio_player = HoldAudioPlayer(orchestrator_ref.audio_manager)

        llm = LLMProcessor(
            llm_port=llm_port,
            config=config,
            conversation_history=conversation_history,
            context=context_data,
            execute_tool_use_case=execute_tool_use_case,
            trace_id=stream_id,
            hold_audio_player=hold_audio_player,
            transcript_callback=transcript_callback # [FEEDBACK] Direct Reporting
        )

        # 5. TTS Processor
        tts = TTSProcessor(tts_port, config)

        # 6. Metrics Processor
        metrics = MetricsProcessor(config)

        # 7. Output Sink
        output_sink = PipelineOutputSink(orchestrator_ref)

        # Assemble Pipeline
        processors = [stt, vad, agg, llm, tts, metrics, output_sink]
        logger.info(f"🏭 [Factory] Pipeline assembled with {len(processors)} processors")

        return PipelineService(processors)
