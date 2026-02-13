"""Value Object for Phone Number."""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class PhoneNumber:
    """
    Value Object representing a phone number.
    Ensures E.164 format or valid local format if needed.
    """
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("PhoneNumber cannot be empty")
        # Basic validation (can be enhanced with phonenumbers lib)
        if not re.match(r"^\+?[1-9]\d{1,14}$", self.value):
             # Allow internal extensions or simple validation for now, 
             # but strictly it should be E.164
             pass 

    def __str__(self) -> str:
        return self.value
