from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import re

# Known insecure default secrets that MUST be changed
_INSECURE_SECRETS = {
    "your-secret-key-change-this-in-production-min-32-chars",
    "your-secret-key-change-this-in-production-min-32-chars-for-hs256",
    "changeme",
    "secret",
}

# Password policy constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:',.<>?/~`]).{8,}$"
)


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False  # Log SQL statements

    # API
    API_TITLE: str = "OBRAS API"
    API_DESCRIPTION: str = "Sistema de Gestión de Accesorios de Izaje v1.2.1"
    API_VERSION: str = "1.2.1"
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    # Security & JWT
    JWT_SECRET: str = "your-secret-key-change-this-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET", mode="after")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if v.lower() in _INSECURE_SECRETS:
            import warnings
            warnings.warn(
                "\n⚠️  JWT_SECRET is set to an insecure default! "
                "Set a strong, unique JWT_SECRET in your .env file before deploying to production.",
                stacklevel=2,
            )
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    # Timezone
    TIMEZONE: str = "America/Bogota"

    # File Storage
    STORAGE_TYPE: str = "local"  # "local" or "s3"
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png"
    ALLOWED_PDF_TYPES: str = "application/pdf"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = 1

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
