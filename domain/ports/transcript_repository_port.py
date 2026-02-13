"""
Port (Interface) for Transcript Persistence.
"""
from abc import ABC, abstractmethod

class TranscriptRepositoryPort(ABC):
    """
    Port for saving conversation transcripts.
    """
    
    @abstractmethod
    async def save(self, call_id: int, role: str, content: str) -> None:
        """
        Save a single transcript entry.
        
        Args:
            call_id: The ID of the associated call.
            role: The speaker role (e.g., 'user', 'assistant', 'system').
            content: The text content.
        """
        pass
