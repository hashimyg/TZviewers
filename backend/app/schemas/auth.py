import re
import uuid
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AdminLogin(BaseModel):
    """
    Input validation firewall for the Admin Login payload.
    Enforces format normalization and corporate password complexity rules.
    """
    # Automatically strips leading/trailing whitespaces across string values
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=12, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Enforces strict lowercase normalization and clean character matches.
        """
        normalized = v.lower()
        if not re.fullmatch(r"[a-z0-9_-]+", normalized):
            raise ValueError("Username must contain only lowercase alphanumeric characters, underscores, or hyphens")
        return normalized

    @field_validator("password")
    @classmethod
    def enforce_strict_password_policy(cls, v: str) -> str:
        """
        SECURITY RESILIENCE: Enforces strict administrative password complexity rules.
        Password spaces are explicitly allowed and preserved.
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter (a-z)")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one numeric digit (0-9)")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`[\]\\/;']", v):
            raise ValueError("Password must contain at least one special character")
        return v


class Token(BaseModel):
    """
    Standardized OAuth2 token response schema.
    Explicitly provides expires_in value to help client interfaces orchestrate rotations.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=3600, description="Token lifespan execution window in seconds.")


class TokenData(BaseModel):
    """
    Internal schema mapping token payloads during request validation.
    Uses RFC 7519 'sub' layout coupled with tracking IDs for absolute identity binding.
    """
    sub: str | None = Field(default=None, description="The subject identifier (Admin username).")
    user_id: uuid.UUID | None = Field(default=None, description="The precise native database tracking ID.")
