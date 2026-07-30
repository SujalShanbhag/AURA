from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


logger = logging.getLogger("aura.repository.user")


class UserRepository:
    """
    User database repository.

    Responsible only for database access.
    Business logic belongs in AuthService.
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
        email: str,
        username: str,
        full_name: str,
        password_hash: str,
    ) -> User:

        user = User(
            email=email.lower().strip(),
            username=username.lower().strip(),
            full_name=full_name.strip(),
            password_hash=password_hash,
        )

        self.db.add(user)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    # =========================================================
    # Read
    # =========================================================

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        return await self.db.get(
            User,
            user_id,
        )

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.email == email.lower().strip()
            )
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.username == username.lower().strip()
            )
        )

        return result.scalar_one_or_none()

    async def exists_by_email(
        self,
        email: str,
    ) -> bool:

        result = await self.db.execute(
            select(
                exists().where(
                    User.email == email.lower().strip()
                )
            )
        )

        return bool(result.scalar())

    async def exists_by_username(
        self,
        username: str,
    ) -> bool:

        result = await self.db.execute(
            select(
                exists().where(
                    User.username == username.lower().strip()
                )
            )
        )

        return bool(result.scalar())

    async def list_users(
        self,
        *,
        limit: int = 100,
    ) -> list[User]:

        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
        )

        return list(result.scalars().all())

    # =========================================================
    # Update
    # =========================================================

    async def update_last_login(
        self,
        user: User,
        login_time: datetime,
    ) -> User:

        user.last_login_at = login_time

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update_password(
        self,
        user: User,
        password_hash: str,
    ) -> User:

        user.password_hash = password_hash

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def verify_email(
        self,
        user: User,
    ) -> User:

        user.is_verified = True

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def activate(
        self,
        user: User,
    ) -> User:

        user.is_active = True

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def deactivate(
        self,
        user: User,
    ) -> User:

        user.is_active = False

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def save(
        self,
        user: User,
    ) -> User:

        await self.db.flush()
        await self.db.refresh(user)

        return user

    # =========================================================
    # Delete
    # =========================================================

    async def delete(
        self,
        user: User,
    ) -> None:

        await self.db.delete(user)

        await self.db.flush()