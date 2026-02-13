"""
Port (Interface) for Call Management Persistence.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Keeping CallRecord as a minimal DTO for the Port for now, 
# but ideally this should return a Domain Entity.
@dataclass
class CallRecord:
     id: int
     stream_id: str
     client_type: str
     started_at: datetime
     ended_at: Optional[datetime] = None
     duration_seconds: Optional[float] = None
     status: str = "active"

class CallRepositoryPort(ABC):
    """
    Port for persisting and retrieving call session data.
    """

    @abstractmethod
    async def create_call(
        self,
        stream_id: str,
        client_type: str,
        metadata: dict
    ) -> CallRecord:
        """
        Create a new call record.
        """
        pass

    @abstractmethod
    async def end_call(self, call_id: int) -> None:
        """
        Mark a call as ended/completed.
        """
        pass

    @abstractmethod
    async def get_call(self, call_id: int) -> Optional[CallRecord]:
        """
        Retrieve a call record by its database ID.
        """
        pass

    @abstractmethod
    async def update_call_extraction(self, call_id: int, extracted_data: dict) -> None:
        """
        Update the call record with post-call analysis data.
        """
        pass
    
    @abstractmethod
    async def delete_call(self, call_id: int) -> None:
        """
        Delete a call record and its associated transcripts.
        
        Args:
            call_id: The ID of the call to delete.
        """
        pass
