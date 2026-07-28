from __future__ import annotations

import uuid
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams

from app.memory.models import MemorySearchResult


class QdrantMemory:
    """
    Semantic memory storage.

    Uses Qdrant for:

    - Vector storage
    - Similarity search
    - Meaning-based recall
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        *,
        collection_name: str = "aura_memory",
        vector_size: int = 1536,
    ):
        self.client = client

        self.collection_name = (
            collection_name
        )

        self.vector_size = vector_size


    async def initialize(
        self,
    ) -> None:
        """
        Create Qdrant collection if missing.
        """

        collections = (
            await self.client
            .get_collections()
        )


        exists = any(
            collection.name
            == self.collection_name
            for collection in collections.collections
        )


        if not exists:

            await self.client.create_collection(
                collection_name=(
                    self.collection_name
                ),

                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )


    async def store_memory(
        self,
        *,
        user_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Store semantic memory vector.
        """

        point_id = str(
            uuid.uuid4()
        )


        point = PointStruct(
            id=point_id,

            vector=embedding,

            payload={
                "user_id": user_id,
                "text": text,
                "metadata": (
                    metadata or {}
                ),
            },
        )


        await self.client.upsert(
            collection_name=(
                self.collection_name
            ),

            points=[
                point
            ],
        )


        return point_id



    async def search_memory(
        self,
        *,
        user_id: str,
        embedding: list[float],
        limit: int = 5,
    ) -> list[MemorySearchResult]:
        """
        Search similar memories.
        """

        results = await self.client.search(
            collection_name=(
                self.collection_name
            ),

            query_vector=embedding,

            limit=limit,

            query_filter={
                "must": [
                    {
                        "key": "user_id",
                        "match": {
                            "value": user_id
                        },
                    }
                ]
            },
        )


        memories = []


        for result in results:

            memories.append(
                MemorySearchResult(
                    memory_id=uuid.UUID(
                        str(result.id)
                    ),

                    content=result.payload[
                        "text"
                    ],

                    score=result.score,

                    metadata=(
                        result.payload
                        .get(
                            "metadata",
                            {}
                        )
                    ),
                )
            )


        return memories



    async def delete_memory(
        self,
        point_id: str,
    ) -> None:
        """
        Delete semantic memory.
        """

        await self.client.delete(
            collection_name=(
                self.collection_name
            ),

            points_selector=[
                point_id
            ],
        )