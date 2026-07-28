from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class AIContext(BaseModel):
    """
    Input context provided to AI providers.

    Contains everything required to generate
    a response.
    """

    user_id: UUID

    conversation_id: UUID | None = None

    message: str = Field(
        min_length=1
    )

    system_prompt: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    timestamp: datetime


class TokenUsage(BaseModel):
    """
    Token consumption information.
    """

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0


class AIProviderInfo(BaseModel):
    """
    Information about the AI provider used.
    """

    name: str

    model: str

    latency_ms: float | None = None


class AIResponse(BaseModel):
    """
    Standard response returned by all AI providers.
    """

    content: str

    provider: AIProviderInfo

    usage: TokenUsage = Field(
        default_factory=TokenUsage
    )

    finish_reason: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime