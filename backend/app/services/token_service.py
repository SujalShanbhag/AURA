from __future__ import annotations

from datetime import datetime
from datetime import timezone
from uuid import UUID

from app.core.security import create_access_token
from app.core.security import create_refresh_token
from app.core.security import generate_token_id
from app.core.security import hash_refresh_token
from app.core.security import validate_token
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)


class TokenService:
    """
    Production token lifecycle service.

    Responsibilities:
    - Create access tokens
    - Create refresh tokens
    - Validate refresh tokens
    - Rotate refresh tokens
    - Detect refresh token reuse
    """

    def __init__(
        self,
        refresh_tokens: RefreshTokenRepository,
    ):
        self.refresh_tokens = refresh_tokens


    async def create_token_pair(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        expires_at: datetime,
    ) -> dict:
        """
        Create access + refresh token pair.
        """

        token_id = generate_token_id()

        refresh_token = create_refresh_token(
            str(user_id),
            token_id,
        )

        refresh_record = (
            await self.refresh_tokens.create(
                user_id=user_id,
                session_id=session_id,
                token_hash=hash_refresh_token(
                    refresh_token
                ),
                expires_at=expires_at,
            )
        )

        return {
            "access_token": create_access_token(
                str(user_id)
            ),
            "refresh_token": refresh_token,
            "refresh_token_id": refresh_record.id,
            "token_type": "bearer",
        }


    async def rotate_refresh_token(
        self,
        *,
        refresh_token: str,
        expires_at: datetime,
    ) -> dict:
        """
        Rotate refresh token.

        Old token:
            revoked

        New token:
            created
        """

        payload = validate_token(
            refresh_token,
            "refresh",
        )

        user_id = UUID(
            payload["sub"]
        )

        token_hash = hash_refresh_token(
            refresh_token
        )

        old_token = (
            await self.refresh_tokens.get_by_hash(
                token_hash
            )
        )

        if old_token is None:
            raise ValueError(
                "Refresh token not found."
            )

        if old_token.is_revoked:
            raise ValueError(
                "Refresh token reuse detected."
            )

        now = datetime.now(
            timezone.utc
        )

        await self.refresh_tokens.revoke(
            old_token,
            revoked_at=now,
            reason="rotation",
        )

        new_token_id = generate_token_id()

        new_refresh_token = create_refresh_token(
            str(user_id),
            new_token_id,
        )

        new_record = (
            await self.refresh_tokens.create(
                user_id=user_id,
                session_id=old_token.session_id,
                token_hash=hash_refresh_token(
                    new_refresh_token
                ),
                expires_at=expires_at,
                parent_token_id=old_token.id,
            )
        )

        await self.refresh_tokens.mark_replaced(
            old_token,
            now,
        )

        return {
            "access_token": create_access_token(
                str(user_id)
            ),
            "refresh_token": new_refresh_token,
            "refresh_token_id": new_record.id,
            "token_type": "bearer",
        }