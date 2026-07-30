from __future__ import annotations

import logging
from typing import Any
from uuid import UUID, uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.memory.models import MemorySearchResult


logger = logging.getLogger(
    "aura.memory.qdrant"
)


class QdrantMemory:
    """
    Qdrant semantic memory manager.

    Handles:
    - Vector storage
    - Semantic search
    - User filtering
    - Memory deletion
    - Collection lifecycle

    Does NOT generate embeddings.
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        *,
        collection_name: str,
        vector_size: int,
    ) -> None:

        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size

    # ==========================================================
    # Collection
    # ==========================================================

    async def initialize(self) -> None:
        """
        Create collection if it doesn't already exist.
        """

        try:

            collections = await self.client.get_collections()

            exists = any(
                collection.name == self.collection_name
                for collection in collections.collections
            )

            if exists:
                return

            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(
                "Created Qdrant collection '%s'.",
                self.collection_name,
            )

        except Exception as exc:

            logger.exception(
                "Failed to initialize Qdrant."
            )

            raise RuntimeError(
                "Unable to initialize Qdrant."
            ) from exc

    # ==========================================================
    # Store Memory
    # ==========================================================

    async def store_memory(
        self,
        *,
        user_id: UUID,
        memory_id: UUID,
        content: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Store vector memory.
        """

        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        if len(embedding) != self.vector_size:
            raise ValueError(
                f"Embedding size must be {self.vector_size}."
            )

        point_id = str(uuid4())

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "user_id": str(user_id),
                "memory_id": str(memory_id),
                "content": content,
                "metadata": metadata or {},
            },
        )

        await self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
            wait=True,
        )

        logger.info(
            "Stored vector memory.",
            extra={
                "point_id": point_id,
            },
        )

        return point_id

    # ==========================================================
    # Search
    # ==========================================================

    async def search(
        self,
        *,
        user_id: UUID | str,
        embedding: list[float],
        limit: int = 5,
    ) -> list[MemorySearchResult]:
        """
        Semantic search.
        """

        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(
                            value=str(user_id)
                        ),
                    )
                ]
            ),
            limit=limit,
        )

        memories: list[MemorySearchResult] = []

        for result in results:

            payload = result.payload or {}

            try:

                memory_id = payload.get(
                    "memory_id"
                )

                if memory_id is None:
                    continue

                memories.append(
                    MemorySearchResult(
                        memory_id=UUID(memory_id),
                        content=payload.get(
                            "content",
                            "",
                        ),
                        score=result.score,
                        metadata=payload.get(
                            "metadata",
                            {},
                        ),
                    )
                )

            except Exception:

                logger.warning(
                    "Invalid Qdrant payload skipped."
                )

        return memories

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    async def search_memory(
        self,
        *,
        user_id: UUID | str,
        embedding: list[float],
        limit: int = 5,
    ) -> list[MemorySearchResult]:

        return await self.search(
            user_id=user_id,
            embedding=embedding,
            limit=limit,
        )

    # ==========================================================
    # Delete
    # ==========================================================

    async def delete_memory(
        self,
        point_id: str,
    ) -> None:
        """
        Delete one vector.
        """

        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=[point_id],
            wait=True,
        )

    async def delete_user_memories(
        self,
        user_id: UUID | str,
    ) -> None:
        """
        Delete all vectors belonging to a user.
        """

        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(
                            value=str(user_id)
                        ),
                    )
                ]
            ),
            wait=True,
        )

    # ==========================================================
    # Health
    # ==========================================================

    async def health_check(self) -> bool:
        """
        Verify Qdrant connectivity.
        """

        try:

            await self.client.get_collections()

            return True

        except Exception:

            logger.exception(
                "Qdrant health check failed."
            )

            return False

    # ==========================================================
    # Cleanup
    # ==========================================================

    async def close(self) -> None:
        """
        Close Qdrant client.
        """

        await self.client.close()