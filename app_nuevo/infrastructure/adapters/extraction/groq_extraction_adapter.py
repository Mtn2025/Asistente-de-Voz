import logging
import json
from typing import Any, List, Dict

from app_nuevo.domain.ports.extraction_port import ExtractionPort
from app_nuevo.infrastructure.config.settings import settings
# We need an http client. We can use httpx directly or a shared client.
# LEGACY used 'app.core.http_client'. We should use a standard library or framework client.
# For now, we'll use httpx as it's standard in this stack.
import httpx

logger = logging.getLogger(__name__)

class GroqExtractionAdapter(ExtractionPort):
    """
    Adapter to handle post-call data extraction using Groq LLM.
    Implements ExtractionPort.
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile" # Updated to versatile as per settings
        self.api_url = f"{settings.GROQ_API_BASE}/chat/completions"

    async def extract_post_call(self, stream_id: str, conversation_history: List[Dict[str, str]]) -> Any:
        """
        Analyze conversation history and extract structured data.
        """
        if not conversation_history:
            logger.warning(f"⚠️ [EXTRACTION] No history to extract for session {stream_id}")
            return {}

        logger.info(f"🔍 [EXTRACTION] Analyzing {len(conversation_history)} messages for session {stream_id}")

        # Format history for prompt
        dialogue_text = "\n".join([f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}" for msg in conversation_history])

        # Schema Definition (Shared Contract)
        schema = {
            "summary": "Resumen breve de la conversación (1-2 frases).",
            "intent": "agendar_cita | consulta | queja | irrelevante | buzon",
            "sentiment": "positive | neutral | negative",
            "extracted_entities": {
                "name": "Nombre del usuario (si se mencionó)",
                "phone": "Teléfono alternativo (si se mencionó)",
                "email": "Correo (si se mencionó)",
                "appointment_date": "Fecha ISO (si se agendó)"
            },
            "next_action": "follow_up | do_nothing"
        }

        system_prompt = (
            "Eres un analista experto de llamadas. "
            "Tu tarea es extraer información estructurada del siguiente diálogo en formato JSON estricto. "
            "No inventes datos. Si no hay datos, usa null.\n\n"
            f"SCHEMA ESPERADO:\n{json.dumps(schema, indent=2)}"
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"DIÁLOGO:\n{dialogue_text}"}
                ],
                "temperature": 0.1, # Deterministic
                "response_format": {"type": "json_object"}
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                extracted_data = json.loads(content)
                logger.info(f"✅ [EXTRACTION] Success: {extracted_data.get('intent', 'unknown')}")
                return extracted_data

        except Exception as e:
            logger.error(f"❌ [EXTRACTION] Failed: {e}")
            return {}
