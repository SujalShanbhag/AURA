from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from app.memory.models import ConversationMemory
from app.memory.postgres_memory import PostgresMemory
from app.memory.qdrant_memory import QdrantMemory
from app.memory.redis_memory import RedisMemory


logger = logging.getLogger(
    "aura.memory.manager"
)


class MemoryManager:
    """
    Unified memory interface.

    Coordinates

    - Redis (short-term memory)
    - PostgreSQL (persistent memory)
    - Qdrant (semantic memory)
    """

    def __init__(
        self,
        *,
        redis_memory: RedisMemory,
        postgres_memory: PostgresMemory,
        qdrant_memory: QdrantMemory,
    ):
        self.redis = redis_memory
        self.postgres = postgres_memory
        self.qdrant = qdrant_memory

    # ---------------------------------------------------------
    # Conversation Memory
    # ---------------------------------------------------------

    async def remember_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        message: str,
        metadata: dict | None = None,
    ) -> None:
        """
        Store a conversation message.
        """

        memory = ConversationMemory(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            message=message,
            metadata=metadata or {},
            created_at=datetime.now(
                timezone.utc,
            ),
        )

        await asyncio.gather(
            self.redis.add_message(
                memory
            ),
            self.postgres.save_conversation(
                memory
            ),
        )

    # ---------------------------------------------------------
    # User Facts
    # ---------------------------------------------------------

    async def remember_fact(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ):
        """
        Store permanent user knowledge.
        """

        record = await self.postgres.save_user_memory(
            user_id=user_id,
            content=content,
            importance=importance,
            metadata=metadata,
        )

        try:
            await self.qdrant.store_memory(
                user_id=str(user_id),
                content=content,
                metadata=metadata or {},
            )

        except Exception:

            logger.exception(
                "Failed to store semantic memory."
            )

        return record

    # ---------------------------------------------------------
    # Recent Conversation
    # ---------------------------------------------------------

    async def get_recent_context(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> list[dict]:

        return await self.redis.get_recent_messages(
            user_id=user_id,
            conversation_id=conversation_id,
        )

    # ---------------------------------------------------------
    # Long-Term Memory
    # ---------------------------------------------------------

    async def get_long_term_memory(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ):

        return await self.postgres.get_user_memories(
            user_id=user_id,
            limit=limit,
        )

    # ---------------------------------------------------------
    # Semantic Search
    # ---------------------------------------------------------

    async def search_semantic_memory(
        self,
        *,
        user_id: UUID,
        embedding: list[float],
        limit: int = 5,
    ):

        return await self.qdrant.search_memory(
            user_id=str(user_id),
            embedding=embedding,
            limit=limit,
        )

    # ---------------------------------------------------------
    # Unified AI Context
    # ---------------------------------------------------------

    async def build_context(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> dict:
        """
        Build the complete AI memory context.
        """

        recent, long_term = await asyncio.gather(
            self.get_recent_context(
                user_id=user_id,
                conversation_id=conversation_id,
            ),
            self.get_long_term_memory(
                user_id=user_id,
            ),
        )

        return {
            "recent_history": recent,
            "semantic_memory": [
                memory.content
                for memory in long_term
            ],
        }

    # ---------------------------------------------------------
    # Session Cleanup
    # ---------------------------------------------------------

    async def clear_session_memory(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> None:

        await self.redis.clear_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    async def memory_stats(
        self,
        *,
        user_id: UUID,
    ) -> dict:

        return {
            "recent_messages": await self.redis.message_count(
                user_id=user_id,
            ),
            "long_term_memories": await self.postgres.memory_count(
                user_id=user_id,
            ),
        }