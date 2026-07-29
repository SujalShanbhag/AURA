from __future__ import annotations

import logging
from uuid import UUID
from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import FieldCondition
from qdrant_client.models import Filter
from qdrant_client.models import MatchValue
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams

from app.memory.models import MemorySearchResult


logger = logging.getLogger(
    "aura.memory.qdrant"
)


class QdrantMemory:
    """
    Semantic memory repository.

    Responsibilities:

    - Store vectors
    - Search vectors
    - Delete vectors
    - Create collection

    Does NOT generate embeddings.
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        *,
        collection_name: str,
        vector_size: int,
    ):
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size

    async def initialize(self) -> None:
        """
        Create collection if it does not exist.
        """

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

    async def store_memory(
        self,
        *,
        user_id: UUID,
        memory_id: UUID,
        text: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> str:
        """
        Store semantic memory.
        """

        point_id = str(uuid4())

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "user_id": str(user_id),
                "memory_id": str(memory_id),
                "text": text,
                "metadata": metadata or {},
            },
        )

        await self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=[point],
        )

        logger.info(
            "Stored semantic memory",
            extra={
                "point_id": point_id,
            },
        )

        return point_id

    async def search(
        self,
        *,
        user_id: UUID,
        embedding: list[float],
        limit: int = 5,
    ) -> list[MemorySearchResult]:
        """
        Semantic similarity search.
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

        memories: list[
            MemorySearchResult
        ] = []

        for result in results:

            payload = result.payload or {}

            memories.append(
                MemorySearchResult(
                    memory_id=UUID(
                        payload["memory_id"]
                    ),
                    content=payload["text"],
                    score=result.score,
                    metadata=payload.get(
                        "metadata",
                        {},
                    ),
                )
            )

        return memories

    async def delete(
        self,
        point_id: str,
    ) -> None:
        """
        Delete vector from Qdrant.
        """

        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=[
                point_id
            ],
            wait=True,
        )

        logger.info(
            "Deleted semantic memory",
            extra={
                "point_id": point_id,
            },
        )

    async def health_check(
        self,
    ) -> bool:
        """
        Verify Qdrant availability.
        """

        try:
            await self.client.get_collections()
            return True

        except Exception:
            logger.exception(
                "Qdrant unavailable"
            )
            return False