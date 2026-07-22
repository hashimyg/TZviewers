import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class ContactCreate(BaseModel):
    """
    Input validation firewall for public contact entries.
    Gracefully sanitizes inputs and handles single-name format profiles safely.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: Optional[str] = Field(default="", min_length=0, max_length=50)
    phone_number: str = Field(..., description="Tanzanian mobile number")
    consent_given: bool = Field(...)

    @field_validator("first_name", "last_name")
    @classmethod
    def sanitize_names(cls, v: str) -> str:
        if v is None:
            return ""
        # Neutralize HTML/Script markup to prevent XSS exploits
        return re.sub(r"<[^>]*>", "", v).strip()

    @field_validator("phone_number")
    @classmethod
    def validate_and_normalize_tz_phone(cls, v: str) -> str:
        digits = re.sub(r"[\s\-\(\)]", "", v)
        if re.match(r"^\+255\d{9}$", digits):
            return digits
        if re.match(r"^255\d{9}$", digits):
            return f"+{digits}"
        if re.match(r"^0\d{9}$", digits):
            return f"+255{digits[1:]}"
        raise ValueError("Invalid Tanzanian mobile phone number format.")

    @field_validator("consent_given")
    @classmethod
    def enforce_legal_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Explicit legal consent is required to register.")
        return v

class ContactResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone_number: str
    is_approved: bool
    terms_version: str

    model_config = ConfigDict(from_attributes=True)
