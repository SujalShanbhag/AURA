from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_token_id,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.session_repository import (
    SessionRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.auth import LoginRequest
from app.schemas.auth import RegisterRequest


class AuthService:
    """
    Production authentication business service.

    Handles:
    - Registration
    - Login
    - Session creation
    - Refresh token creation

    Database access is delegated to repositories.
    Transaction ownership remains here.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    async def register(
        self,
        request: RegisterRequest,
    ):
        """
        Register a new user.
        """

        async with self.db.begin():

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
        Authenticate user and create:
        - Session
        - Refresh token
        - Access token
        """

        async with self.db.begin():

            user = await self.users.get_by_email(
                request.email
            )

            if user is None:
                raise ValueError(
                    "Invalid credentials."
                )

            if not user.is_active:
                raise ValueError(
                    "Account is disabled."
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

            await self.users.update_last_login(
                user=user,
                login_time=now,
            )

            expires_at = (
                now
                + timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                )
            )

            session = await self.sessions.create(
                user_id=user.id,
                device_name=request.device_name,
                device_type=request.device_type,
                operating_system=request.operating_system,
                browser=request.browser,
                ip_address=request.ip_address,
                country=None,
                city=None,
                user_agent=request.user_agent,
                is_current=True,
                expires_at=expires_at,
            )

            token_id = generate_token_id()

            refresh_token = create_refresh_token(
                str(user.id),
                token_id,
            )

            refresh = await self.refresh_tokens.create(
                user_id=user.id,
                session_id=session.id,
                token_hash=hash_refresh_token(
                    refresh_token
                ),
                expires_at=expires_at,
            )

            access_token = create_access_token(
                str(user.id)
            )

        return {
            "user": user,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
            "session_id": str(session.id),
            "refresh_token_id": str(refresh.id),
        }