from pathlib import Path
from typing import List, Literal, Union, Optional
from pydantic import (
    AnyHttpUrl,
    BeforeValidator,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

# Absolute tracking path reference mapping pointing strictly to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def validate_cors_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str):
        if v.strip() == "*":
            return ["*"]
        if not v.startswith("["):
            return [i.strip() for i in v.split(",")]
    if isinstance(v, list):
        return v
    raise ValueError(f"Invalid CORS format: {v}")


class Settings(BaseSettings):
    # Instructs Pydantic to read parameters directly from the root file block if present
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 1. ENVIRONMENT CONFIGURATIONS
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Tanzanian VCF Platform"
    API_V1_STR: str = "/api"

    # 2. PERSISTENT STORAGE PARAMETERS (Set completely to Optional to clear reload crashes)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[SecretStr] = None
    POSTGRES_DB: Optional[str] = None
    
    # Reads the active data connection URL string directly from environment scopes
    DATABASE_URL: PostgresDsn

    # 3. CACHE CONFIGURATIONS
    REDIS_URL: RedisDsn

    # 4. CRYPTOGRAPHIC ACCESS SECURITY SETTINGS
    JWT_SECRET: SecretStr
    ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret_strength(cls, v: SecretStr) -> SecretStr:
        secret_raw = v.get_secret_value()
        if len(secret_raw) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    # 5. CORS FIREWALL CHANNELS
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(validate_cors_origins)
    ] = ["*"]


# Central app configuration instantiation instance
settings = Settings()
