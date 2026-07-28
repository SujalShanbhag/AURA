from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.core.security import verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.auth import RegisterRequest
from app.services.session_service import SessionService
from app.services.token_service import TokenService


class AuthService:
    """
    Production authentication coordinator.

    Responsibilities:
    - User registration
    - Login orchestration
    - Logout orchestration
    - Refresh token orchestration

    Business logic is delegated to:
    - UserRepository
    - SessionService
    - TokenService
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.users = UserRepository(
            db
        )

        self.sessions = SessionService(
            db
        )

        self.tokens = TokenService(
            self.sessions.sessions.db
            and self.sessions.sessions
        )


    async def register(
        self,
        request: RegisterRequest,
    ):
        """
        Register a new user.
        """

        existing_email = await self.users.get_by_email(
            request.email
        )

        if existing_email:
            raise ValueError(
                "Email already exists."
            )

        existing_username = await self.users.get_by_username(
            request.username
        )

        if existing_username:
            raise ValueError(
                "Username already exists."
            )

        user = await self.users.create(
            email=request.email,
            username=request.username,
            full_name=request.full_name,
            password_hash=hash_password(
                request.password
            ),
        )

        return user


    async def login(
        self,
        request: LoginRequest,
    ):
        """
        Authenticate user and create
        session + token pair.
        """

        user = await self.users.get_by_email(
            request.email
        )

        if user is None:
            raise ValueError(
                "Invalid credentials."
            )

        if not user.is_active:
            raise ValueError(
                "Account disabled."
            )

        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid credentials."
            )

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        session = await self.sessions.create_session(
            user_id=user.id,
            device_name=request.device_name,
            device_type=request.device_type,
            operating_system=request.operating_system,
            browser=request.browser,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            expires_at=expires_at,
        )

        tokens = await self.tokens.create_token_pair(
            user_id=user.id,
            session_id=session.id,
            expires_at=expires_at,
        )

        await self.users.update_last_login(
            user=user,
            login_time=now,
        )

        return {
            "user": user,
            "tokens": tokens,
        }


    async def refresh(
        self,
        refresh_token: str,
    ):
        """
        Rotate refresh token and
        issue new access token.
        """

        expires_at = (
            datetime.now(
                timezone.utc
            )
            + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        return await self.tokens.rotate_refresh_token(
            refresh_token=refresh_token,
            expires_at=expires_at,
        )


    async def logout(
        self,
        session_id,
    ):
        """
        Logout current device.
        """

        return await self.sessions.logout(
            session_id
        )


    async def logout_all(
        self,
        user_id,
    ):
        """
        Logout all devices.
        """

        return await self.sessions.logout_all(
            user_id
        )