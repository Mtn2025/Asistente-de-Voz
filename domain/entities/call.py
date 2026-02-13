"""
Domain Entity: Call
Represents a voice call session with its lifecycle and state.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from app.domain.value_objects.call_id import CallId
from app.domain.value_objects.call_context import CallMetadata

class CallStatus(Enum):
    """Possible states of a call session."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ENDING = "ending"
    ENDED = "ended"
    FAILED = "failed"

@dataclass
class Call:
    """
    Rich Domain Entity representing a Call.
    
    Attributes:
        id: Unique identifier (Value Object).
        metadata: Contextual metadata (Value Object).
        status: Current lifecycle state.
        started_at: Timestamp when call started.
        ended_at: Timestamp when call ended (if applicable).
    """
    id: CallId
    metadata: CallMetadata
    status: CallStatus = CallStatus.INITIALIZING
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    
    def start(self) -> None:
        """Mark the call as active."""
        if self.status != CallStatus.INITIALIZING:
             # In a real scenario, we might raise a DomainError here
             pass 
        self.status = CallStatus.ACTIVE

    def end(self, timestamp: datetime = None) -> None:
        """
        Transition the call to ENDED state.
        
        Args:
            timestamp: Optional explicit timestamp. Defaults to UTC now.
        """
        if self.status in (CallStatus.ENDED, CallStatus.FAILED):
            return

        self.status = CallStatus.ENDED
        self.ended_at = timestamp or datetime.utcnow()

    def fail(self, timestamp: datetime = None) -> None:
        """Mark the call as FAILED."""
        self.status = CallStatus.FAILED
        self.ended_at = timestamp or datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Check if call is currently active."""
        return self.status == CallStatus.ACTIVE

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate call duration in seconds."""
        if not self.ended_at:
            return None
        return (self.ended_at - self.started_at).total_seconds()
