from __future__ import annotations

from datetime import datetime
from datetime import timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.session_repository import SessionRepository


class SessionService:
    """
    Production session management service.

    Handles:
    - Creating sessions
    - Validating sessions
    - Revoking sessions
    - Multi-device logout
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.sessions = SessionRepository(db)


    async def create_session(
        self,
        *,
        user_id: UUID,
        device_name: str | None,
        device_type: str | None,
        operating_system: str | None,
        browser: str | None,
        ip_address: str | None,
        user_agent: str | None,
        expires_at: datetime,
    ):
        """
        Create a new user session.
        """

        return await self.sessions.create(
            user_id=user_id,
            device_name=device_name,
            device_type=device_type,
            operating_system=operating_system,
            browser=browser,
            ip_address=ip_address,
            country=None,
            city=None,
            user_agent=user_agent,
            is_current=True,
            expires_at=expires_at,
        )


    async def validate_session(
        self,
        session_id: UUID,
    ):
        """
        Validate an active session.
        """

        session = await self.sessions.get_by_id(
            session_id
        )

        if session is None:
            raise ValueError(
                "Session not found."
            )

        now = datetime.now(
            timezone.utc
        )

        if session.expires_at <= now:
            raise ValueError(
                "Session expired."
            )

        if not session.is_current:
            raise ValueError(
                "Session revoked."
            )

        return session


    async def logout(
        self,
        session_id: UUID,
    ):
        """
        Logout from one device.
        """

        session = await self.sessions.get_by_id(
            session_id
        )

        if session is None:
            return False

        await self.sessions.revoke(
            session,
            revoked_at=datetime.now(
                timezone.utc
            ),
        )

        return True


    async def logout_all(
        self,
        user_id: UUID,
    ):
        """
        Logout all user devices.
        """

        sessions = await self.sessions.get_user_sessions(
            user_id
        )

        now = datetime.now(
            timezone.utc
        )

        revoked = 0

        for session in sessions:

            if session.is_current:

                await self.sessions.revoke(
                    session,
                    revoked_at=now,
                )

                revoked += 1

        return {
            "revoked_sessions": revoked
        }


    async def get_active_sessions(
        self,
        user_id: UUID,
    ):
        """
        Return active sessions for a user.
        """

        return await self.sessions.get_user_sessions(
            user_id
        )