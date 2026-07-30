from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """
    Refresh token database operations.

    Handles:
    - Token storage
    - Token rotation
    - Token revocation
    - Cleanup
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # =========================================================
    # Create
    # =========================================================

    async def create(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        token_hash: str,
        expires_at: datetime,
        parent_token_id: UUID | None = None,
    ) -> RefreshToken:
        """
        Create refresh token record.
        """

        token = RefreshToken(
            user_id=user_id,
            session_id=session_id,
            token_hash=token_hash,
            expires_at=expires_at,
            parent_token_id=parent_token_id,
        )

        self.db.add(token)

        await self.db.flush()
        await self.db.refresh(token)

        return token

    # =========================================================
    # Retrieval
    # =========================================================

    async def get_by_id(
        self,
        token_id: UUID,
    ) -> RefreshToken | None:

        return await self.db.get(
            RefreshToken,
            token_id,
        )

    async def get_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()

    async def get_valid_token(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        """
        Return a valid (non-expired and non-revoked)
        refresh token.
        """

        token = await self.get_by_hash(token_hash)

        if token is None:
            return None

        now = datetime.now(timezone.utc)

        expires_at = token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if token.is_revoked:
            return None

        if expires_at <= now:
            return None

        return token

    async def list_active_for_user(
        self,
        user_id: UUID,
    ) -> list[RefreshToken]:

        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False),
            )
            .order_by(
                RefreshToken.created_at.desc()
            )
        )

        return list(result.scalars().all())

    # =========================================================
    # Revocation
    # =========================================================

    async def revoke(
        self,
        token: RefreshToken,
        *,
        reason: str,
        revoked_at: datetime,
    ) -> RefreshToken:
        """
        Revoke a refresh token.
        """

        if not token.is_revoked:
            token.is_revoked = True
            token.revoked_reason = reason
            token.revoked_at = revoked_at

            await self.db.flush()

        return token

    async def revoke_by_id(
        self,
        token_id: UUID,
        reason: str,
    ) -> bool:

        token = await self.get_by_id(token_id)

        if token is None:
            return False

        if token.is_revoked:
            return True

        token.is_revoked = True
        token.revoked_reason = reason
        token.revoked_at = datetime.now(
            timezone.utc
        )

        await self.db.flush()

        return True

    async def revoke_chain(
        self,
        *,
        root_token_id: UUID,
        reason: str,
        revoked_at: datetime,
    ) -> int:
        """
        Revoke an entire refresh-token chain.
        """

        revoked = 0
        current_ids = [root_token_id]

        while current_ids:

            result = await self.db.execute(
                select(RefreshToken).where(
                    or_(
                        RefreshToken.id.in_(current_ids),
                        RefreshToken.parent_token_id.in_(current_ids),
                    )
                )
            )

            tokens = result.scalars().all()

            if not tokens:
                break

            current_ids = []

            for token in tokens:

                if not token.is_revoked:
                    token.is_revoked = True
                    token.revoked_reason = reason
                    token.revoked_at = revoked_at
                    revoked += 1

                current_ids.append(token.id)

        await self.db.flush()

        return revoked

    async def mark_replaced(
        self,
        token: RefreshToken,
        replaced_at: datetime,
    ) -> RefreshToken:
        """
        Mark token as replaced during rotation.
        """

        token.replaced_at = replaced_at

        await self.db.flush()

        return token

    # =========================================================
    # Cleanup
    # =========================================================

    async def cleanup_expired(
        self,
        now: datetime,
    ) -> int:
        """
        Delete expired refresh tokens.
        """

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.expires_at < now
            )
        )

        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            await self.db.delete(token)

        await self.db.flush()

        return len(expired_tokens)

    async def delete(
        self,
        token: RefreshToken,
    ) -> None:

        await self.db.delete(token)
        await self.db.flush()