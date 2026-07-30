from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ============================================================
# Memory Types
# ============================================================

class MemoryType(str, Enum):
    """
    Supported memory categories.
    """

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    CONVERSATION = "conversation"
    SEMANTIC = "semantic"


# ============================================================
# Base Memory Record
# ============================================================

class MemoryRecord(BaseModel):
    """
    Common memory structure.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID | None = None

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

    @field_validator("content")
    @classmethod
    def validate_content(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Content cannot be empty."
            )

        return value


# ============================================================
# Conversation Memory
# ============================================================

class ConversationMemory(BaseModel):
    """
    Chat message memory.

    Stored in:
    - PostgreSQL
    - Redis
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID | None = None

    user_id: UUID

    conversation_id: UUID

    role: str = Field(
        min_length=1,
        max_length=32,
    )

    content: str = Field(
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

    @field_validator("role")
    @classmethod
    def validate_role(
        cls,
        value: str,
    ) -> str:
        value = value.strip().lower()

        allowed = {
            "user",
            "assistant",
            "system",
            "tool",
        }

        if value not in allowed:
            raise ValueError(
                f"Invalid role '{value}'."
            )

        return value

    @field_validator("content")
    @classmethod
    def validate_content(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Content cannot be empty."
            )

        return value


# ============================================================
# Semantic Memory
# ============================================================

class SemanticMemory(BaseModel):
    """
    Vector database memory object.

    Stored in Qdrant.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UUID

    memory_id: UUID

    content: str

    embedding: list[float]

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("content")
    @classmethod
    def validate_content(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Content cannot be empty."
            )

        return value


# ============================================================
# Search Result
# ============================================================

class MemorySearchResult(BaseModel):
    """
    Qdrant similarity search result.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    memory_id: UUID

    content: str

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("content")
    @classmethod
    def validate_content(
        cls,
        value: str,
    ) -> str:
        return value.strip()