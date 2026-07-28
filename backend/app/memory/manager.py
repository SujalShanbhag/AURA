from __future__ import annotations

from datetime import datetime
from datetime import timezone
from uuid import UUID

from app.memory.models import ConversationMemory
from app.memory.postgres_memory import PostgresMemory
from app.memory.qdrant_memory import QdrantMemory
from app.memory.redis_memory import RedisMemory


class MemoryManager:
    """
    Unified memory interface for AURA.

    Combines:

    - Redis short-term memory
    - PostgreSQL long-term memory
    - Qdrant semantic memory
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



    async def remember_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        message: str,
        metadata: dict | None = None,
    ):
        """
        Save conversation into all required layers.
        """

        memory = ConversationMemory(
            user_id=user_id,

            conversation_id=conversation_id,

            role=role,

            message=message,

            metadata=metadata or {},

            created_at=datetime.now(
                timezone.utc
            ),
        )


        # Short-term memory
        await self.redis.add_message(
            memory
        )


        # Long-term memory
        await self.postgres.save_conversation(
            memory
        )



    async def remember_fact(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ):
        """
        Store important user information.

        Example:
        "User likes AI projects"
        """

        return await self.postgres.save_user_memory(
            user_id=user_id,
            content=content,
            importance=importance,
            metadata=metadata,
        )



    async def get_recent_context(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> list[dict]:
        """
        Get active conversation context.
        """

        return await self.redis.get_recent_messages(
            user_id=user_id,
            conversation_id=conversation_id,
        )



    async def get_long_term_memory(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ):
        """
        Retrieve permanent memories.
        """

        return await self.postgres.get_user_memories(
            user_id=user_id,
            limit=limit,
        )



    async def search_semantic_memory(
        self,
        *,
        user_id: UUID,
        embedding: list[float],
        limit: int = 5,
    ):
        """
        Search Qdrant memories.
        """

        return await self.qdrant.search_memory(
            user_id=str(user_id),
            embedding=embedding,
            limit=limit,
        )



    async def clear_session_memory(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ):
        """
        Remove temporary conversation memory.
        """

        await self.redis.clear_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
        )