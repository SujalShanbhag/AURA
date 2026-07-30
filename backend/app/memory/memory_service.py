from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.embedding_service import EmbeddingService
from app.memory.models import ConversationMemory
from app.memory.postgres_memory import PostgresMemory
from app.memory.qdrant_memory import QdrantMemory


logger = logging.getLogger("aura.memory.service")


class MemoryService:
    """
    Production memory orchestration layer.

    Coordinates:

    PostgreSQL
        |
        +--> Conversation memory
        |
        +--> Long-term memory

    Embedding Service
        |
        v

    Qdrant
        |
        +--> Semantic search
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        embedding_service: EmbeddingService,
        qdrant_memory: QdrantMemory,
    ) -> None:

        self.db = db
        self.embedding_service = embedding_service
        self.qdrant = qdrant_memory
        self.postgres = PostgresMemory(db)

    # ==========================================================
    # Conversation Memory
    # ==========================================================

    async def save_conversation(
        self,
        conversation: ConversationMemory,
    ):
        """
        Save conversation to PostgreSQL.
        """

        try:
            result = await self.postgres.save_conversation(
                conversation
            )

            await self.db.commit()

            return result

        except Exception:
            await self.db.rollback()

            logger.exception(
                "Failed to save conversation."
            )

            raise

    # ==========================================================
    # Long-Term Memory
    # ==========================================================

    async def save_long_term_memory(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Save long-term memory to PostgreSQL and Qdrant.
        """

        content = content.strip()

        if not content:
            raise ValueError(
                "Memory content cannot be empty."
            )

        if not 0.0 <= importance <= 1.0:
            raise ValueError(
                "Importance must be between 0 and 1."
            )

        metadata = metadata or {}

        try:
            memory = await self.postgres.save_user_memory(
                user_id=user_id,
                content=content,
                importance=importance,
                metadata=metadata,
            )

            embedding = await (
                self.embedding_service.create_embedding(
                    content
                )
            )

            point_id = await self.qdrant.store_memory(
                user_id=user_id,
                memory_id=memory.id,
                content=content,
                embedding=embedding,
                metadata=metadata,
            )

            await self.postgres.update_qdrant_point(
                memory=memory,
                point_id=point_id,
            )

            await self.db.commit()

            logger.info(
                "Long-term memory stored.",
                extra={
                    "user_id": str(user_id),
                    "memory_id": str(memory.id),
                },
            )

            return memory

        except Exception:
            await self.db.rollback()

            logger.exception(
                "Failed to save long-term memory."
            )

            raise

    # ==========================================================
    # Retrieval
    # ==========================================================

    async def conversation_history(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 20,
    ):
        """
        Retrieve conversation history.
        """

        try:
            return await self.postgres.get_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=limit,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve conversation."
            )
            return []

    async def long_term_memories(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ):
        """
        Retrieve stored long-term memories.
        """

        try:
            return await self.postgres.get_user_memories(
                user_id=user_id,
                limit=limit,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve memories."
            )
            return []

    async def semantic_search(
        self,
        *,
        user_id: UUID,
        query: str,
        limit: int = 5,
    ):
        """
        Semantic search using Qdrant.
        """

        query = query.strip()

        if not query:
            return []

        try:
            embedding = await (
                self.embedding_service.create_embedding(
                    query
                )
            )

            return await self.qdrant.search_memory(
                user_id=str(user_id),
                embedding=embedding,
                limit=limit,
            )

        except Exception:
            logger.exception(
                "Semantic search failed."
            )

            return []

    # ==========================================================
    # Delete
    # ==========================================================

    async def delete_memory(
        self,
        memory_id: UUID,
    ) -> bool:
        """
        Delete memory from PostgreSQL.
        """

        try:
            result = await self.postgres.delete_memory(
                memory_id
            )

            await self.db.commit()

            return result

        except Exception:
            await self.db.rollback()

            logger.exception(
                "Failed to delete memory."
            )

            raise

    # ==========================================================
    # Health
    # ==========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Check memory subsystem health.
        """

        try:
            return await self.qdrant.health_check()

        except Exception:
            logger.exception(
                "Memory health check failed."
            )

            return False

    # ==========================================================
    # Cleanup
    # ==========================================================

    async def close(self) -> None:
        """
        Cleanup resources.
        """

        return None