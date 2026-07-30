from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
)

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Memory(Base):
    """
    Permanent AURA memory table.

    Stores:

    - Conversation history
    - Long-term memories
    - Semantic memory references
    """

    __tablename__ = "memories"

    # =========================================================
    # Primary Key
    # =========================================================

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # =========================================================
    # Ownership
    # =========================================================

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    conversation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # =========================================================
    # Memory Information
    # =========================================================

    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
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
        nullable=False,
        default=0.5,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    qdrant_point_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # =========================================================
    # Timestamps
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # =========================================================
    # Relationships
    # =========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="memories",
        lazy="selectin",
    )

    # =========================================================
    # Constraints & Indexes
    # =========================================================

    __table_args__ = (
        CheckConstraint(
            "importance >= 0 AND importance <= 1",
            name="check_memory_importance_range",
        ),
        Index(
            "idx_memory_user_type",
            "user_id",
            "memory_type",
        ),
        Index(
            "idx_memory_conversation_time",
            "user_id",
            "conversation_id",
            "created_at",
        ),
        Index(
            "idx_memory_qdrant",
            "qdrant_point_id",
        ),
        Index(
            "idx_memory_created",
            "created_at",
        ),
    )

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(self) -> str:
        return (
            f"<Memory("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"type={self.memory_type}, "
            f"importance={self.importance}"
            f")>"
        )