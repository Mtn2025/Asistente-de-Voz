"""
Domain Entity: Conversation
Represents the history of messages in a dialogue.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass(frozen=True)
class Message:
    """Immutable Value Object representing a single message."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = None

@dataclass
class Conversation:
    """
    Rich Domain Entity representing a Conversation History.
    
    Encapsulates the list of messages and provides methods to manipulate and format them.
    """
    messages: List[Message] = field(default_factory=list)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a new message to the history."""
        self.messages.append(Message(role=role, content=content, metadata=metadata))

    def add_system_message(self, content: str) -> None:
        """Add a system instruction."""
        self.messages.append(Message(role="system", content=content))

    def add_user_message(self, content: str) -> None:
        """Add a user message."""
        self.messages.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant response."""
        self.messages.append(Message(role="assistant", content=content))

    def get_context_for_llm(self) -> List[Dict[str, str]]:
        """
        Format conversation for LLM consumption.
        Returns list of {"role": ..., "content": ...} dicts.
        """
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def last_message(self) -> Optional[Message]:
        return self.messages[-1] if self.messages else None
