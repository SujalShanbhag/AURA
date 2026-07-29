from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.embedding_service import EmbeddingService
from app.memory.postgres_memory import PostgresMemory
from app.memory.qdrant_memory import QdrantMemory


logger = logging.getLogger(
    "aura.memory.service"
)


class MemoryService:
    """
    Production memory service.

    Coordinates:

    - PostgreSQL
    - Embedding generation
    - Qdrant vector storage

    The AI Brain should communicate ONLY with this service.
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        embedding_service: EmbeddingService,
        qdrant_memory: QdrantMemory,
    ):
        self.db = db

        self.embedding_service = (
            embedding_service
        )

        self.qdrant = (
            qdrant_memory
        )

        self.postgres = (
            PostgresMemory(db)
        )


    async def save_fact(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ):
        """
        Save important long-term memory.

        Workflow:

        PostgreSQL
              ↓
        Embedding
              ↓
        Qdrant
              ↓
        PostgreSQL Update
        """

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
                user_id=str(user_id),
                text=content,
                embedding=embedding,
                metadata={
                    "memory_id": str(memory.id),
                    "importance": importance,
                    **(metadata or {}),
                },
            )
        )

        memory.qdrant_point_id = point_id

        await self.db.commit()

        await self.db.refresh(memory)

        logger.info(
            "Long-term memory stored",
            extra={
                "memory_id": str(memory.id),
                "user_id": str(user_id),
            },
        )

        return memory


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

        return await self.qdrant.search_memory(
            user_id=str(user_id),
            embedding=embedding,
            limit=limit,
        )


    async def save_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        message: str,
        metadata: dict | None = None,
    ):
        """
        Save conversation history.
        """

        from app.memory.models import ConversationMemory

        conversation = (
            ConversationMemory(
                user_id=user_id,
                conversation_id=conversation_id,
                role=role,
                message=message,
                metadata=metadata or {},
            )
        )

        return await self.postgres.save_conversation(
            conversation
        )


    async def conversation_history(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 50,
    ):
        """
        Retrieve conversation history.
        """

        return await self.postgres.get_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=limit,
        )


    async def user_memories(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ):
        """
        Retrieve important memories.
        """

        return await self.postgres.get_user_memories(
            user_id=user_id,
            limit=limit,
        )