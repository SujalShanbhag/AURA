from __future__ import annotations

import json
from datetime import datetime
from datetime import timezone
from uuid import UUID

from redis.asyncio import Redis

from app.memory.models import ConversationMemory


class RedisMemory:
    """
    Short-term memory storage.

    Uses Redis for:
    - Recent conversation context
    - Temporary user state
    - Fast retrieval

    Data automatically expires.
    """

    def __init__(
        self,
        redis: Redis,
        *,
        ttl_seconds: int = 86400,
        max_messages: int = 20,
    ):
        self.redis = redis

        self.ttl_seconds = ttl_seconds

        self.max_messages = max_messages


    def _conversation_key(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ) -> str:
        """
        Generate isolated Redis key.
        """

        return (
            f"aura:memory:"
            f"{user_id}:"
            f"{conversation_id}"
        )


    async def add_message(
        self,
        memory: ConversationMemory,
    ) -> None:
        """
        Store a conversation message.
        """

        key = self._conversation_key(
            memory.user_id,
            memory.conversation_id,
        )


        payload = {
            "role": memory.role,
            "message": memory.message,
            "metadata": memory.metadata,
            "created_at": (
                memory.created_at
                .isoformat()
            ),
        }


        await self.redis.rpush(
            key,
            json.dumps(payload),
        )


        await self.redis.ltrim(
            key,
            -self.max_messages,
            -1,
        )


        await self.redis.expire(
            key,
            self.ttl_seconds,
        )


    async def get_recent_messages(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> list[dict]:
        """
        Retrieve recent conversation context.
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


        return [
            json.loads(message)
            for message in messages
        ]


    async def clear_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> None:
        """
        Delete temporary memory.
        """

        key = self._conversation_key(
            user_id,
            conversation_id,
        )


        await self.redis.delete(
            key
        )


    async def update_state(
        self,
        *,
        user_id: UUID,
        state: dict,
        ttl_seconds: int | None = None,
    ):
        """
        Store temporary user state.
        """

        key = (
            f"aura:state:"
            f"{user_id}"
        )


        await self.redis.set(
            key,
            json.dumps(state),
            ex=(
                ttl_seconds
                or self.ttl_seconds
            ),
        )


    async def get_state(
        self,
        user_id: UUID,
    ) -> dict:
        """
        Retrieve temporary state.
        """

        key = (
            f"aura:state:"
            f"{user_id}"
        )


        value = await self.redis.get(
            key
        )


        if value is None:
            return {}


        return json.loads(
            value
        )