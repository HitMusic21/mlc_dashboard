"""Core configuration for BWARM Dashboard using Pydantic Settings."""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project
    PROJECT_NAME: str = Field(default="bwarm_dashboard", description="Project name")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/bwarm_dev",
        description="PostgreSQL database URL with asyncpg driver",
    )

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="API port")
    API_PREFIX: str = Field(default="/api/v1", description="API route prefix")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Security & JWT
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        min_length=32,
        description="Secret key for JWT encoding (MUST be changed in production)",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, ge=1, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, ge=1, description="Refresh token expiration in days"
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validate that SECRET_KEY has been changed from default in production."""
        # Allow default in DEBUG mode for development
        if v == "change-this-secret-key-in-production":
            # Check if DEBUG mode is enabled (if available in context)
            debug = info.data.get("DEBUG", False)
            if not debug:
                raise ValueError(
                    "SECRET_KEY must be changed from default value in production. "
                    "Generate a secure key with: openssl rand -hex 32"
                )

        # Ensure minimum security: no common/weak patterns
        weak_patterns = ["secret", "password", "12345", "test", "demo", "example"]
        if any(pattern in v.lower() for pattern in weak_patterns):
            raise ValueError(
                "SECRET_KEY contains weak patterns. "
                "Generate a secure key with: openssl rand -hex 32"
            )

        return v

    # CORS
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend URL")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    REDIS_DB: int = Field(default=0, ge=0, description="Redis database number")
    REDIS_PASSWORD: str = Field(default="", description="Redis password")

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL from components."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0", description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0", description="Celery result backend URL"
    )

    # Elasticsearch
    ELASTICSEARCH_HOST: str = Field(default="localhost", description="Elasticsearch host")
    ELASTICSEARCH_PORT: int = Field(
        default=9200, ge=1, le=65535, description="Elasticsearch port"
    )
    ELASTICSEARCH_INDEX_PREFIX: str = Field(
        default="bwarm_", description="Elasticsearch index prefix"
    )

    @property
    def ELASTICSEARCH_URL(self) -> str:
        """Construct Elasticsearch URL from components."""
        return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=500, ge=1, le=2000, description="Max upload size in MB"
    )
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=["csv", "xlsx", "xls", "json", "xml"],
        description="Allowed file extensions",
    )

    @field_validator("ALLOWED_FILE_EXTENSIONS", mode="before")
    @classmethod
    def parse_file_extensions(cls, v):
        """Parse file extensions from comma-separated string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        """Convert max upload size to bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Catalog Matching
    MATCH_CONFIDENCE_THRESHOLD: float = Field(
        default=0.6, ge=0.0, le=1.0, description="Minimum match confidence threshold"
    )
    MAX_MATCHES_PER_TRACK: int = Field(
        default=10, ge=1, le=100, description="Maximum matches to return per track"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")


# Global settings instance
settings = Settings()
