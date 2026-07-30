from __future__ import annotations

import logging

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_token_id,
    hash_password,
    hash_refresh_token,
    validate_token,
    verify_password,
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest

logger = logging.getLogger("aura.auth.service")


class AuthService:
    """
    Authentication business layer.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    # =========================================================
    # Register
    # =========================================================

    async def register(
        self,
        request: RegisterRequest,
    ):

        try:

            if await self.users.get_by_email(request.email):
                raise ValueError("Email already exists.")

            if await self.users.get_by_username(request.username):
                raise ValueError("Username already exists.")

            user = await self.users.create(
                email=request.email,
                username=request.username,
                full_name=request.full_name,
                password_hash=hash_password(request.password),
            )

            await self.db.commit()

            return user

        except Exception:

            await self.db.rollback()
            logger.exception("User registration failed.")
            raise

    # =========================================================
    # Login
    # =========================================================

    async def login(
        self,
        request: LoginRequest,
        *,
        ip_address: str,
        user_agent: str,
    ):

        try:

            user = await self.users.get_by_email(request.email)

            if user is None:
                raise ValueError("Invalid credentials.")

            if not user.is_active:
                raise ValueError("Account disabled.")

            if not verify_password(
                request.password,
                user.password_hash,
            ):
                raise ValueError("Invalid credentials.")

            now = datetime.now(timezone.utc)

            await self.users.update_last_login(
                user,
                now,
            )

            expires_at = now + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            session = await self.sessions.create(
                user_id=user.id,
                device_name=request.device_name,
                device_type=request.device_type,
                operating_system=request.operating_system,
                browser=request.browser,
                ip_address=ip_address,
                country=None,
                city=None,
                user_agent=user_agent,
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
                token_hash=hash_refresh_token(refresh_token),
                expires_at=expires_at,
            )

            await self.sessions.attach_refresh_token(
                session,
                refresh.id,
            )

            access_token = create_access_token(
                str(user.id)
            )

            await self.db.commit()

            return {
                "user": user,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                },
            }

        except Exception:

            await self.db.rollback()
            logger.exception("Login failed.")
            raise

    # =========================================================
    # Refresh Token Rotation
    # =========================================================

    async def refresh(
        self,
        refresh_token: str,
    ):

        try:

            payload = validate_token(
                refresh_token,
                "refresh",
            )

            user_id = UUID(payload["sub"])

            token_hash = hash_refresh_token(
                refresh_token
            )

            stored = await self.refresh_tokens.get_by_hash(
                token_hash
            )

            if stored is None:
                raise ValueError("Invalid refresh token.")

            if stored.is_revoked:
                raise ValueError("Refresh token revoked.")

            if stored.expires_at < datetime.now(timezone.utc):
                raise ValueError("Refresh token expired.")

            access_token = create_access_token(
                str(user_id)
            )

            # -------------------------------
            # Rotate refresh token
            # -------------------------------

            new_token_id = generate_token_id()

            new_refresh_token = create_refresh_token(
                str(user_id),
                new_token_id,
            )

            new_record = await self.refresh_tokens.create(
                user_id=user_id,
                session_id=stored.session_id,
                token_hash=hash_refresh_token(
                    new_refresh_token
                ),
                expires_at=stored.expires_at,
                parent_token_id=stored.id,
            )

            await self.refresh_tokens.revoke(
                stored.id,
                reason="rotated",
            )

            session = await self.sessions.get(
                stored.session_id
            )

            if session is not None:

                await self.sessions.attach_refresh_token(
                    session,
                    new_record.id,
                )

            await self.db.commit()

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }

        except Exception:

            await self.db.rollback()
            logger.exception("Refresh token failed.")
            raise

    # =========================================================
    # Logout
    # =========================================================

    async def logout(
        self,
        session_id: UUID,
    ):

        try:

            await self.sessions.revoke(
                session_id
            )

            await self.db.commit()

            return True

        except Exception:

            await self.db.rollback()
            logger.exception("Logout failed.")
            raise

    # =========================================================
    # Logout All
    # =========================================================

    async def logout_all(
        self,
        user_id: UUID,
    ):

        try:

            await self.sessions.revoke_all(
                user_id
            )

            await self.db.commit()

            return True

        except Exception:

            await self.db.rollback()
            logger.exception("Logout all failed.")
            raise