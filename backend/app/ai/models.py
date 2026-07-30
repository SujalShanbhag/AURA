from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ==========================================================
# AI Context
# ==========================================================

class AIContext(BaseModel):
    """
    Complete request context passed to AI providers.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
    )

    request_id: UUID = Field(
        default_factory=uuid4,
    )

    user_id: UUID

    conversation_id: UUID | None = None

    message: str = Field(
        min_length=1,
        max_length=50000,
    )

    system_prompt: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        return value or {}


# ==========================================================
# Token Usage
# ==========================================================

class TokenUsage(BaseModel):
    """
    AI token consumption.
    """

    prompt_tokens: int = Field(
        default=0,
        ge=0,
    )

    completion_tokens: int = Field(
        default=0,
        ge=0,
    )

    total_tokens: int = Field(
        default=0,
        ge=0,
    )

    @model_validator(mode="after")
    def compute_total(self):
        if self.total_tokens == 0:
            self.total_tokens = (
                self.prompt_tokens
                + self.completion_tokens
            )
        return self


# ==========================================================
# Provider Information
# ==========================================================

class AIProviderInfo(BaseModel):
    """
    AI provider execution metadata.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
    )

    name: str

    model: str

    latency_ms: float | None = None

    supports_streaming: bool = True

    supports_tools: bool = False

    context_window: int | None = None


# ==========================================================
# AI Response
# ==========================================================

class AIResponse(BaseModel):
    """
    Standard AI provider response.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    content: str = ""

    provider: AIProviderInfo

    usage: TokenUsage = Field(
        default_factory=TokenUsage,
    )

    finish_reason: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    @field_validator("content")
    @classmethod
    def validate_content(
        cls,
        value: str | None,
    ) -> str:
        return (value or "").strip()

    @field_validator("metadata")
    @classmethod
    def validate_metadata(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        return value or {}


# ==========================================================
# Streaming Chunk
# ==========================================================

class AIStreamChunk(BaseModel):
    """
    Single streaming response chunk.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    content: str = ""

    done: bool = False

    provider: str | None = None

    model: str | None = None

    finish_reason: str | None = None


# ==========================================================
# Provider Health
# ==========================================================

class AIHealthStatus(BaseModel):
    """
    Health status of an AI provider.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    provider: str

    healthy: bool

    model: str | None = None

    latency_ms: float | None = None

    error: str | None = None