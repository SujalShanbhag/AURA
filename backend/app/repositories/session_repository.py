from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    """
    Database operations for user sessions.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        user_id: UUID,
        refresh_token_id: UUID | None = None,
        device_name: str,
        device_type: str,
        operating_system: str,
        browser: str | None,
        ip_address: str,
        country: str | None,
        city: str | None,
        user_agent: str,
        is_current: bool,
        expires_at: datetime,
    ) -> Session:

        now = datetime.now(timezone.utc)

        session = Session(
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            device_name=device_name,
            device_type=device_type,
            operating_system=operating_system,
            browser=browser,
            ip_address=ip_address,
            country=country,
            city=city,
            user_agent=user_agent,
            is_current=is_current,
            is_revoked=False,
            expires_at=expires_at,
            created_at=now,
            last_seen_at=now,
        )

        self.db.add(session)

        await self.db.flush()
        await self.db.refresh(session)

        return session

    async def get_by_id(
        self,
        session_id: UUID,
    ) -> Session | None:

        return await self.db.get(
            Session,
            session_id,
        )

    async def list_user_sessions(
        self,
        user_id: UUID,
    ) -> list[Session]:

        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
                Session.expires_at > now,
            )
            .order_by(Session.last_seen_at.desc())
        )

        return list(result.scalars().all())

    async def attach_refresh_token(
        self,
        session: Session,
        refresh_token_id: UUID,
    ) -> Session:

        session.refresh_token_id = refresh_token_id

        await self.db.flush()
        await self.db.refresh(session)

        return session

    async def update_last_seen(
        self,
        session: Session,
        timestamp: datetime,
    ) -> Session:

        session.last_seen_at = timestamp

        await self.db.flush()
        await self.db.refresh(session)

        return session

    async def revoke(
        self,
        session_id: UUID,
    ) -> bool:

        session = await self.get_by_id(session_id)

        if session is None:
            return False

        session.is_revoked = True
        session.is_current = False
        session.revoked_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(session)

        return True

    async def revoke_all(
        self,
        user_id: UUID,
    ) -> None:

        result = await self.db.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
            )
        )

        now = datetime.now(timezone.utc)

        for session in result.scalars():
            session.is_revoked = True
            session.is_current = False
            session.revoked_at = now

        await self.db.flush()

    async def delete(
        self,
        session: Session,
    ) -> None:

        await self.db.delete(session)
        await self.db.flush()