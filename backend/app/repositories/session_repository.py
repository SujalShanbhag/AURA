from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: UUID,
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

        session = Session(
            user_id=user_id,
            device_name=device_name,
            device_type=device_type,
            operating_system=operating_system,
            browser=browser,
            ip_address=ip_address,
            country=country,
            city=city,
            user_agent=user_agent,
            is_current=is_current,
            expires_at=expires_at,
        )

        self.db.add(session)

        await self.db.flush()
        await self.db.refresh(session)

        return session

    async def get_by_id(
        self,
        session_id: UUID,
    ) -> Session | None:

        return await self.db.get(Session, session_id)

    async def list_user_sessions(
        self,
        user_id: UUID,
    ) -> list[Session]:

        result = await self.db.execute(
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
            )
            .order_by(
                Session.last_seen_at.desc()
            )
        )

        return list(result.scalars().all())

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
        session: Session,
        revoked_at: datetime,
    ) -> Session:

        session.is_revoked = True
        session.revoked_at = revoked_at
        session.is_current = False

        await self.db.flush()
        await self.db.refresh(session)

        return session

    async def revoke_all(
        self,
        user_id: UUID,
        revoked_at: datetime,
    ) -> None:

        result = await self.db.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
            )
        )

        sessions = result.scalars().all()

        for session in sessions:
            session.is_revoked = True
            session.revoked_at = revoked_at
            session.is_current = False

        await self.db.flush()

    async def delete(
        self,
        session: Session,
    ) -> None:

        await self.db.delete(session)
        await self.db.flush()