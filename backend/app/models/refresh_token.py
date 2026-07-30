from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


class RefreshToken(Base):
    """
    Refresh token storage.

    Supports:
    - Token rotation
    - Token revocation
    - Token history tracking
    """

    __tablename__ = "refresh_tokens"

    # =========================================================
    # Primary Key
    # =========================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # =========================================================
    # Foreign Keys
    # =========================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    parent_token_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "refresh_tokens.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # =========================================================
    # Token Data
    # =========================================================

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    revoked_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # Dates
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    replaced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================================================
    # Relationships
    # =========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
        lazy="selectin",
    )

    # Session that owns this token
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="refresh_tokens",
        foreign_keys=[session_id],
        lazy="selectin",
    )

    # Session.current_refresh_token
    current_for_session: Mapped["Session | None"] = relationship(
        "Session",
        foreign_keys="Session.refresh_token_id",
        uselist=False,
        viewonly=True,
    )

    # Token rotation chain
    parent: Mapped["RefreshToken | None"] = relationship(
        "RefreshToken",
        remote_side=[id],
        foreign_keys=[parent_token_id],
        back_populates="children",
        lazy="selectin",
    )

    children: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # =========================================================
    # Indexes
    # =========================================================

    __table_args__ = (
        Index(
            "idx_refresh_token_user_active",
            "user_id",
            "is_revoked",
        ),
        Index(
            "idx_refresh_token_session",
            "session_id",
        ),
        Index(
            "idx_refresh_token_expiry",
            "expires_at",
        ),
    )

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(self) -> str:
        return (
            f"<RefreshToken("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"revoked={self.is_revoked}"
            f")>"
        )