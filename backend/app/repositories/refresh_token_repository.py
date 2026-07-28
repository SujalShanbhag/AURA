from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        token_hash: str,
        expires_at: datetime,
        parent_token_id: UUID | None = None,
    ) -> RefreshToken:

        token = RefreshToken(
            user_id=user_id,
            session_id=session_id,
            token_hash=token_hash,
            expires_at=expires_at,
            parent_token_id=parent_token_id,
        )

        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)

        return token

    async def get_by_id(
        self,
        token_id: UUID,
    ) -> RefreshToken | None:

        return await self.db.get(RefreshToken, token_id)

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

    async def revoke(
        self,
        token: RefreshToken,
        *,
        reason: str,
        revoked_at: datetime,
    ) -> RefreshToken:

        token.is_revoked = True
        token.revoked_reason = reason
        token.revoked_at = revoked_at

        await self.db.commit()
        await self.db.refresh(token)

        return token

    async def mark_replaced(
        self,
        token: RefreshToken,
        replaced_at: datetime,
    ) -> RefreshToken:

        token.replaced_at = replaced_at

        await self.db.commit()
        await self.db.refresh(token)

        return token

    async def revoke_chain(
        self,
        root_token_id: UUID,
        *,
        reason: str,
        revoked_at: datetime,
    ) -> None:

        result = await self.db.execute(
            select(RefreshToken).where(
                (RefreshToken.id == root_token_id)
                | (RefreshToken.parent_token_id == root_token_id)
            )
        )

        tokens = result.scalars().all()

        for token in tokens:
            token.is_revoked = True
            token.revoked_reason = reason
            token.revoked_at = revoked_at

        await self.db.commit()

    async def delete(
        self,
        token: RefreshToken,
    ) -> None:

        await self.db.delete(token)
        await self.db.commit()

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

    async def cleanup_expired(
        self,
        now: datetime,
    ) -> int:

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.expires_at < now
            )
        )

        expired = result.scalars().all()

        count = 0

        for token in expired:
            await self.db.delete(token)
            count += 1

        await self.db.commit()

        return count