from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class MemoryType:
    """
    Supported memory categories.
    """

    SHORT_TERM = "short_term"

    LONG_TERM = "long_term"

    SEMANTIC = "semantic"


class MemoryRecord(BaseModel):
    """
    Base memory object stored by AURA.
    """

    user_id: UUID

    memory_type: str

    content: str = Field(
        min_length=1
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime

    updated_at: datetime


class ConversationMemory(BaseModel):
    """
    Conversation history memory.

    Stored permanently in PostgreSQL.
    """

    user_id: UUID

    conversation_id: UUID

    role: str

    message: str

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime


class SemanticMemory(BaseModel):
    """
    Vector memory representation.

    Stored in Qdrant.
    """

    user_id: UUID

    memory_id: UUID

    text: str

    embedding: list[float]

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class MemorySearchResult(BaseModel):
    """
    Result returned from memory retrieval.
    """

    memory_id: UUID

    content: str

    score: float

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )