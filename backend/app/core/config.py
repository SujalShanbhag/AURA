from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    AURA application configuration.

    Loads values from .env
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ========================================================
    # Application
    # ========================================================

    ENVIRONMENT: str = "development"

    APP_NAME: str = "AURA"

    APP_VERSION: str = "1.0.0"

    DEBUG: bool = False

    # ========================================================
    # Database
    # ========================================================

    DATABASE_URL: str

    # ========================================================
    # Redis
    # ========================================================

    REDIS_URL: str = "redis://localhost:6379"

    REDIS_HOST: str = "localhost"

    REDIS_PORT: int = 6379

    REDIS_DB: int = 0

    # ========================================================
    # Authentication / JWT
    # ========================================================

    JWT_SECRET: str

    JWT_ALGORITHM: str = "HS256"

    JWT_ISSUER: str = "AURA"

    JWT_AUDIENCE: str = "AURA_USERS"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ========================================================
    # AI Providers
    # ========================================================

    AI_PRIMARY_PROVIDER: str = "gemini"

    AI_FALLBACK_PROVIDERS: list[str] = Field(
        default_factory=lambda: [
            "openai",
            "ollama",
        ]
    )

    AI_MAX_RETRIES: int = 3

    AI_REQUEST_TIMEOUT: float = 120.0

    # ========================================================
    # Gemini
    # ========================================================

    GEMINI_API_KEY: str = ""

    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ========================================================
    # OpenAI
    # ========================================================

    OPENAI_API_KEY: str = ""

    OPENAI_MODEL: str = "gpt-4.1-mini"

    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ========================================================
    # Anthropic
    # ========================================================

    ANTHROPIC_API_KEY: str = ""

    # ========================================================
    # Ollama
    # ========================================================

    OLLAMA_ENABLED: bool = False

    OLLAMA_BASE_URL: str = "http://localhost:11434"

    OLLAMA_MODEL: str = "llama3.1"

    # ========================================================
    # Qdrant
    # ========================================================

    QDRANT_URL: str = "http://localhost:6333"

    QDRANT_API_KEY: str | None = None

    QDRANT_COLLECTION: str = "aura_memory"

    QDRANT_VECTOR_SIZE: int = 1536

    # ========================================================
    # CORS
    # ========================================================

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8081",
        ]
    )


settings = Settings()