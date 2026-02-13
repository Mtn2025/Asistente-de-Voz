"""
Domain Entity: Transcript
Represents a persistent record of a conversation segment.
"""
from dataclasses import dataclass, field
from datetime import datetime
from app.domain.value_objects.call_id import CallId

@dataclass(frozen=True)
class Transcript:
    """
    Immutable Entity representing a Transcript entry.
    Unlike 'Message' which is part of an active Conversation in memory,
    Transcript is a record meant for persistence/logs.
    """
    call_id: CallId
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "call_id": str(self.call_id),
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
