"""
Common Schemas for Input Validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class CallLogFilter(BaseModel):
    """
    Schema for filtering call logs.
    Prevents SQL injection in search queries.
    """
    search: str | None = Field(None, max_length=100)
    status: str | None = Field(None, pattern=r'^(completed|failed|in_progress)$')
    limit: int | None = Field(10, ge=1, le=100)
    offset: int | None = Field(0, ge=0)

    @field_validator('search')
    @classmethod
    def sanitize_search(cls, v: str | None) -> str | None:
        """Sanitize search query to prevent SQL injection."""
        if not v:
            return v

        # Remove SQL keywords and special characters
        dangerous_keywords = [
            'select', 'insert', 'update', 'delete', 'drop',
            'union', 'exec', '--', ';', '/*', '*/',
        ]

        v_lower = v.lower()
        for keyword in dangerous_keywords:
            if keyword in v_lower:
                raise ValueError(f"Search contains dangerous keyword: {keyword}")

        # Keep only alphanumeric, spaces, and basic punctuation
        import re
        v = re.sub(r'[^a-zA-Z0-9\s.@_-]', '', v)

        return v.strip()


class PhoneNumberInput(BaseModel):
    """
    Schema for phone number input.
    Validates phone number format.
    """
    phone_number: str = Field(..., min_length=10, max_length=20)

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number contains only safe characters."""
        import re

        # Remove all non-numeric characters except + - ( ) and spaces
        v = re.sub(r'[^0-9+\-() ]', '', v)

        # Must contain at least 10 digits
        digits = re.sub(r'\D', '', v)
        if len(digits) < 10:
            raise ValueError("Phone number must contain at least 10 digits")

        return v.strip()


class EmailInput(BaseModel):
    """
    Schema for email input with built-in validation.
    """
    email: EmailStr

    @field_validator('email')
    @classmethod
    def sanitize_email(cls, v: EmailStr) -> str:
        """Additional sanitization for email."""
        # Convert to lowercase
        email_str = str(v).lower().strip()

        # Reject emails with dangerous patterns
        if '<' in email_str or '>' in email_str:
            raise ValueError("Email contains invalid characters")

        return email_str


class APIKeyRotation(BaseModel):
    """
    Schema for API key rotation.
    Validates new API keys.
    """
    new_api_key: str = Field(..., min_length=32, max_length=128)
    confirm_api_key: str = Field(..., min_length=32, max_length=128)

    @field_validator('new_api_key', 'confirm_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        import re

        # API keys should be alphanumeric + some special chars
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', v):
            raise ValueError("API key contains invalid characters")

        return v

    def __init__(self, **data):
        super().__init__(**data)
        # Validate keys match
        if self.new_api_key != self.confirm_api_key:
            raise ValueError("API keys do not match")
