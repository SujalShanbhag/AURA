from __future__ import annotations

import logging
from typing import List

from openai import AsyncOpenAI

from app.core.config import settings


logger = logging.getLogger(
    "aura.memory.embedding"
)


class EmbeddingService:
    """
    Text embedding generation service.

    Converts text into vector embeddings
    for semantic memory search.

    Supports:
    - OpenAI embeddings
    - Future local embedding models
    """


    def __init__(
        self,
    ):

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = (
            settings.EMBEDDING_MODEL
        )


    async def create_embedding(
        self,
        text: str,
    ) -> List[float]:
        """
        Generate vector embedding.

        Example:

        "I like AI projects"

        becomes:

        [0.23, 0.81, ...]
        """

        if not text.strip():

            raise ValueError(
                "Text cannot be empty."
            )


        try:

            response = (
                await self.client.embeddings.create(
                    model=self.model,
                    input=text,
                )
            )


            return (
                response
                .data[0]
                .embedding
            )


        except Exception as exc:

            logger.exception(
                "Embedding generation failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "Embedding service failed."
            ) from exc



    async def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings in batch.
        """

        if not texts:

            return []


        try:

            response = (
                await self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                )
            )


            return [
                item.embedding
                for item in response.data
            ]


        except Exception as exc:

            logger.exception(
                "Batch embedding failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "Batch embedding failed."
            ) from exc



    async def health_check(
        self,
    ) -> bool:
        """
        Check embedding availability.
        """

        try:

            await self.client.models.list()

            return True


        except Exception:

            return False