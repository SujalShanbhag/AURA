from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.embedding_service import EmbeddingService
from app.memory.models import ConversationMemory
from app.memory.postgres_memory import PostgresMemory
from app.memory.qdrant_memory import QdrantMemory


logger = logging.getLogger(
    "aura.memory.service"
)


class MemoryService:
    """
    Production memory service.

    Coordinates all memory systems.

    Responsibilities

    - PostgreSQL persistence
    - Embedding generation
    - Qdrant synchronization
    - Transaction ownership

    The AI Brain communicates ONLY with this service.
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        embedding_service: EmbeddingService,
        qdrant_memory: QdrantMemory,
    ):
        self.db = db

        self.embedding_service = embedding_service

        self.qdrant = qdrant_memory

        self.postgres = PostgresMemory(db)

    async def save_conversation(
        self,
        conversation: ConversationMemory,
    ):
        """
        Persist a conversation message.

        Conversation history is stored only
        in PostgreSQL.
        """

        try:

            memory = (
                await self.postgres.save_conversation(
                    conversation
                )
            )

            await self.db.commit()

            return memory

        except Exception:

            await self.db.rollback()

            logger.exception(
                "Failed to save conversation."
            )

            raise

    async def save_long_term_memory(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ):
        """
        Save a long-term memory.

        Workflow

        PostgreSQL
              ↓
        Embedding
              ↓
        Qdrant
              ↓
        Update PostgreSQL
              ↓
        Commit
        """

        try:

            memory = (
                await self.postgres.save_user_memory(
                    user_id=user_id,
                    content=content,
                    importance=importance,
                    metadata=metadata,
                )
            )

            embedding = (
                await self.embedding_service.create_embedding(
                    content
                )
            )

            point_id = (
                await self.qdrant.store_memory(
                    user_id=user_id,
                    memory_id=memory.id,
                    text=content,
                    embedding=embedding,
                    metadata=metadata,
                )
            )

            await self.postgres.update_qdrant_point(
                memory=memory,
                point_id=point_id,
            )

            await self.db.commit()

            return memory

        except Exception:

            await self.db.rollback()

            logger.exception(
                "Failed to save long-term memory."
            )

            raise

    async def conversation_history(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 100,
    ):
        """
        Retrieve conversation history.
        """

        return (
            await self.postgres.get_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=limit,
            )
        )

    async def long_term_memories(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ):
        """
        Retrieve stored memories.
        """

        return (
            await self.postgres.get_user_memories(
                user_id=user_id,
                limit=limit,
            )
        )

    async def semantic_search(
        self,
        *,
        user_id: UUID,
        query: str,
        limit: int = 5,
    ):
        """
        Search memories by meaning.
        """

        embedding = (
            await self.embedding_service.create_embedding(
                query
            )
        )

        return (
            await self.qdrant.search(
                user_id=user_id,
                embedding=embedding,
                limit=limit,
            )
        )

    async def health_check(
        self,
    ) -> bool:
        """
        Verify memory subsystem.
        """

        return await self.qdrant.health_check()