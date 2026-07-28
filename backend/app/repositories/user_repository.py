from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        email: str,
        username: str,
        full_name: str,
        password_hash: str,
    ) -> User:
        user = User(
            email=email.lower(),
            username=username,
            full_name=full_name,
            password_hash=password_hash,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.email == email.lower()
            )
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.username == username
            )
        )

        return result.scalar_one_or_none()

    async def update_last_login(
        self,
        user: User,
        login_time,
    ) -> User:
        user.last_login_at = login_time

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_password(
        self,
        user: User,
        password_hash: str,
    ) -> User:
        user.password_hash = password_hash

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def verify_email(
        self,
        user: User,
    ) -> User:
        user.is_verified = True

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def deactivate(
        self,
        user: User,
    ) -> User:
        user.is_active = False

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def activate(
        self,
        user: User,
    ) -> User:
        user.is_active = True

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete(
        self,
        user: User,
    ) -> None:
        await self.db.delete(user)
        await self.db.commit()