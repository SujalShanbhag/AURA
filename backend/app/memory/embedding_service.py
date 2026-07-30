from __future__ import annotations

import logging

from openai import AsyncOpenAI

from app.core.config import settings


logger = logging.getLogger(
    "aura.memory.embedding"
)


class EmbeddingService:
    """
    Text embedding generation service.

    Converts text into vector embeddings for
    semantic memory search.

    Supports:
    - OpenAI Embeddings
    - Future local embedding models
    """

    def __init__(self) -> None:

        self.model = settings.EMBEDDING_MODEL

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
        )

    # ==========================================================
    # Single Embedding
    # ==========================================================

    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate a single embedding.
        """

        text = text.strip()

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        try:

            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )

            embedding = response.data[0].embedding

            logger.debug(
                "Embedding generated (%d dimensions).",
                len(embedding),
            )

            return embedding

        except Exception as exc:

            logger.exception(
                "Embedding generation failed."
            )

            raise RuntimeError(
                "Embedding service failed."
            ) from exc

    # ==========================================================
    # Batch Embeddings
    # ==========================================================

    async def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        cleaned = [
            text.strip()
            for text in texts
            if text.strip()
        ]

        if not cleaned:
            return []

        try:

            response = await self.client.embeddings.create(
                model=self.model,
                input=cleaned,
            )

            embeddings = [
                item.embedding
                for item in response.data
            ]

            logger.debug(
                "Generated %d embeddings.",
                len(embeddings),
            )

            return embeddings

        except Exception as exc:

            logger.exception(
                "Batch embedding generation failed."
            )

            raise RuntimeError(
                "Batch embedding generation failed."
            ) from exc

    # ==========================================================
    # Health Check
    # ==========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify OpenAI connectivity.
        """

        try:

            await self.client.models.list()

            return True

        except Exception:

            logger.exception(
                "Embedding service health check failed."
            )

            return False

    # ==========================================================
    # Cleanup
    # ==========================================================

    async def close(
        self,
    ) -> None:
        """
        Close underlying HTTP client.
        """

        await self.client.close()