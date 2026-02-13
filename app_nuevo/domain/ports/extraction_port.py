"""
Port (Interface) for Post-Call Analysis and Extraction.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict

class ExtractionPort(ABC):
    """
    Port for analyzing call transcripts and extracting structured data.
    """

    @abstractmethod
    async def extract_post_call(self, stream_id: str, conversation_history: List[Dict[str, str]]) -> Any:
        """
        Perform analysis on the completed call conversation.
        
        Args:
            stream_id: Unique identifier for the call stream.
            conversation_history: List of message dictionaries ({role, content}).
            
        Returns:
            Structured extracted data.
        """
        pass
