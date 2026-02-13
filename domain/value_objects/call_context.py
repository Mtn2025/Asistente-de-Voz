"""Value Objects for Call Context."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app_nuevo.domain.value_objects.phone_number import PhoneNumber
from app_nuevo.domain.value_objects.call_id import CallId

@dataclass(frozen=True)
class ContactInfo:
    """
    Contact information from CRM (immutable).
    """
    name: Optional[str] = None
    phone: Optional[PhoneNumber] = None
    email: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

    def to_prompt_context(self) -> str:
        """
        Format contact info for LLM prompt injection.
        
        Returns:
            str: Human-readable context string.
        """
        parts = []
        if self.name:
            parts.append(f"Cliente: {self.name}")
        if self.company:
            parts.append(f"Empresa: {self.company}")
        if self.email:
            parts.append(f"Email: {self.email}")
        if self.notes:
            parts.append(f"Notas: {self.notes}")
        
        return ". ".join(parts) if parts else ""

    @property
    def has_data(self) -> bool:
        """Check if contact has any information."""
        return any([self.name, self.phone, self.email, self.company, self.notes])


@dataclass(frozen=True)
class CallMetadata:
    """
    Call session metadata (immutable).
    """
    session_id: CallId
    client_type: str  # browser, twilio, telnyx
    phone_number: Optional[PhoneNumber] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    campaign_id: Optional[str] = None

    @property
    def is_inbound(self) -> bool:
        return self.phone_number is not None

    @property
    def is_outbound(self) -> bool:
        return self.campaign_id is not None

    @property
    def is_telephony(self) -> bool:
        return self.client_type in ["twilio", "telnyx"]

    @property
    def is_browser(self) -> bool:
        return self.client_type == "browser"

    @property
    def duration_seconds(self) -> float:
        """Calculate call duration so far."""
        return (datetime.utcnow() - self.started_at).total_seconds()
