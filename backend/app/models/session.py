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
    from app.models.refresh_token import RefreshToken
    from app.models.user import User


class Session(Base):
    """
    AURA user device session model.

    Stores:
    - Login devices
    - Active sessions
    - Device information
    - Expiration
    - Revocation tracking
    """

    __tablename__ = "sessions"

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

    refresh_token_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "refresh_tokens.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # =========================================================
    # Device Information
    # =========================================================

    device_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Unknown Device",
    )

    device_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unknown",
    )

    operating_system: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="unknown",
    )

    browser: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ip_address: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    user_agent: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # =========================================================
    # Status
    # =========================================================

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # =========================================================
    # Dates
    # =========================================================

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # =========================================================
    # Relationships
    # =========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
        lazy="selectin",
    )

    # Current refresh token (1:1)
    refresh_token: Mapped["RefreshToken | None"] = relationship(
        "RefreshToken",
        foreign_keys=[refresh_token_id],
        uselist=False,
        lazy="selectin",
        post_update=True,
    )

    # Historical refresh tokens (1:N)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="session",
        foreign_keys="RefreshToken.session_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # =========================================================
    # Constraints & Indexes
    # =========================================================

    __table_args__ = (
        Index(
            "idx_session_user_active",
            "user_id",
            "is_revoked",
        ),
        Index(
            "idx_session_expiry",
            "expires_at",
        ),
        Index(
            "idx_session_last_seen",
            "last_seen_at",
        ),
    )

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(self) -> str:
        return (
            f"<Session("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"device={self.device_name!r}, "
            f"revoked={self.is_revoked}"
            f")>"
        )