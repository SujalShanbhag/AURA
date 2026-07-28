from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Index
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database import Base


class Memory(Base):
    """
    Permanent memory storage model.

    Stores:

    - Conversation history
    - Long-term user memories
    - Future vector references
    """

    __tablename__ = "memories"


    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        index=True,
    )


    user_id: Mapped[UUID] = mapped_column(
        index=True,
        nullable=False,
    )


    conversation_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
        index=True,
    )


    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    role: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )


    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    importance: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )


    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )


    qdrant_point_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


Index(
    "idx_memory_user_type",
    Memory.user_id,
    Memory.memory_type,
)


Index(
    "idx_memory_conversation",
    Memory.user_id,
    Memory.conversation_id,
)