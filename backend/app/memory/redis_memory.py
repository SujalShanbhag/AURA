from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from app.memory.models import ConversationMemory


logger = logging.getLogger(
    "aura.memory.redis"
)


class RedisMemory:
    """
    Redis short-term memory.

    Stores:
    - Recent conversations
    - User session state
    - Temporary cache
    """

    def __init__(
        self,
        redis: Redis,
        *,
        ttl_seconds: int = 86400,
        max_messages: int = 20,
    ) -> None:

        self.redis = redis
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages

    # ==========================================================
    # Keys
    # ==========================================================

    def _conversation_key(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ) -> str:

        return (
            f"aura:memory:"
            f"{user_id}:"
            f"{conversation_id}"
        )

    def _state_key(
        self,
        user_id: UUID,
    ) -> str:

        return (
            f"aura:state:"
            f"{user_id}"
        )

    # ==========================================================
    # Conversation Memory
    # ==========================================================

    async def add_message(
        self,
        memory: ConversationMemory,
    ) -> None:
        """
        Append a message to Redis conversation history.
        """

        key = self._conversation_key(
            memory.user_id,
            memory.conversation_id,
        )

        payload = {
            "role": memory.role,
            "message": memory.message,
            "metadata": memory.metadata,
            "created_at": memory.created_at.isoformat(),
        }

        try:

            async with self.redis.pipeline() as pipe:

                (
                    pipe.rpush(
                        key,
                        json.dumps(payload),
                    )
                    .ltrim(
                        key,
                        -self.max_messages,
                        -1,
                    )
                    .expire(
                        key,
                        self.ttl_seconds,
                    )
                )

                await pipe.execute()

        except Exception:

            logger.exception(
                "Failed to store Redis conversation."
            )

            raise

    async def get_recent_messages(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Retrieve recent conversation history.
        """

        key = self._conversation_key(
            user_id,
            conversation_id,
        )

        messages = await self.redis.lrange(
            key,
            0,
            -1,
        )

        history: list[dict[str, Any]] = []

        for item in messages:

            try:

                if isinstance(item, bytes):
                    item = item.decode("utf-8")

                history.append(
                    json.loads(item)
                )

            except Exception:

                logger.warning(
                    "Skipping invalid Redis message."
                )

        return history

    async def clear_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> None:
        """
        Remove cached conversation.
        """

        await self.redis.delete(
            self._conversation_key(
                user_id,
                conversation_id,
            )
        )

    async def message_count(
        self,
        *,
        user_id: UUID,
    ) -> int:
        """
        Count cached messages.
        """

        pattern = (
            f"aura:memory:{user_id}:*"
        )

        total = 0

        async for key in self.redis.scan_iter(
            match=pattern,
        ):
            total += await self.redis.llen(
                key
            )

        return total

    # ==========================================================
    # User State
    # ==========================================================

    async def update_state(
        self,
        *,
        user_id: UUID,
        state: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Save temporary user state.
        """

        await self.redis.set(
            self._state_key(user_id),
            json.dumps(state),
            ex=ttl_seconds or self.ttl_seconds,
        )

    async def get_state(
        self,
        user_id: UUID,
    ) -> dict[str, Any]:
        """
        Retrieve temporary user state.
        """

        value = await self.redis.get(
            self._state_key(user_id)
        )

        if value is None:
            return {}

        try:

            if isinstance(value, bytes):
                value = value.decode("utf-8")

            return json.loads(value)

        except Exception:

            logger.warning(
                "Invalid Redis state."
            )

            return {}

    async def delete_state(
        self,
        user_id: UUID,
    ) -> None:
        """
        Delete cached user state.
        """

        await self.redis.delete(
            self._state_key(user_id)
        )

    # ==========================================================
    # Utilities
    # ==========================================================

    async def refresh_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> None:
        """
        Refresh conversation TTL.
        """

        await self.redis.expire(
            self._conversation_key(
                user_id,
                conversation_id,
            ),
            self.ttl_seconds,
        )

    # ==========================================================
    # Health
    # ==========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify Redis connectivity.
        """

        try:

            await self.redis.ping()

            return True

        except Exception:

            logger.exception(
                "Redis health check failed."
            )

            return False