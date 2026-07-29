from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MemoryType(str, Enum):
    """
    Supported memory categories.
    """

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    CONVERSATION = "conversation"
    SEMANTIC = "semantic"


class MemoryRecord(BaseModel):
    """
    Base memory model shared across memory providers.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UUID

    memory_type: MemoryType

    content: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    updated_at: datetime | None = None


class ConversationMemory(BaseModel):
    """
    Conversation message exchanged between
    a user and AURA.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UUID

    conversation_id: UUID

    role: str = Field(
        min_length=1,
        max_length=32,
    )

    message: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


class SemanticMemory(BaseModel):
    """
    Memory stored inside the vector database.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UUID

    memory_id: UUID

    text: str

    embedding: list[float]

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class MemorySearchResult(BaseModel):
    """
    Result returned by semantic search.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    memory_id: UUID

    content: str

    score: float

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )