"""Value Object for Call Identifier."""
from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class CallId:
    """
    Unique identifier for a call session.
    
    Attributes:
         value (str): UUID string.
    """
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("CallId cannot be empty")
            
    @classmethod
    def generate(cls) -> 'CallId':
        """Generate a new unique CallId."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value
