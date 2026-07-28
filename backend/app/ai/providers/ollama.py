from __future__ import annotations

import logging
import time
from datetime import datetime
from datetime import timezone
from typing import AsyncIterator

import httpx

from app.ai.models import AIContext
from app.ai.models import AIProviderInfo
from app.ai.models import AIResponse
from app.ai.models import TokenUsage
from app.ai.provider import AIProvider
from app.core.config import settings


logger = logging.getLogger(
    "aura.ai.ollama"
)


class OllamaProvider(AIProvider):
    """
    Local Ollama AI provider.

    Supports:
    - Local model generation
    - Streaming
    - Health checks
    """


    name = "ollama"


    def __init__(
        self,
        model: str | None = None,
    ):
        self.model = (
            model
            or settings.OLLAMA_MODEL
        )

        self.base_url = (
            settings.OLLAMA_BASE_URL
        )


    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Generate response using local model.
        """

        start = time.perf_counter()

        try:

            async with httpx.AsyncClient() as client:

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": context.message,
                        "stream": False,
                    },
                    timeout=120,
                )


                response.raise_for_status()

                data = response.json()


            latency = (
                time.perf_counter()
                - start
            ) * 1000


            return AIResponse(
                content=data.get(
                    "response",
                    "",
                ),

                provider=AIProviderInfo(
                    name=self.name,
                    model=self.model,
                    latency_ms=latency,
                ),

                usage=TokenUsage(),

                created_at=datetime.now(
                    timezone.utc
                ),
            )


        except Exception as exc:

            logger.exception(
                "Ollama generation failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "Ollama provider failed."
            ) from exc



    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:
        """
        Stream local model response.
        """

        try:

            async with httpx.AsyncClient() as client:

                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": context.message,
                        "stream": True,
                    },
                    timeout=120,
                ) as response:

                    async for line in response.aiter_lines():

                        if line:

                            data = (
                                line
                            )

                            if data:

                                yield data


        except Exception as exc:

            logger.exception(
                "Ollama streaming failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "Ollama streaming failed."
            ) from exc



    async def health_check(
        self,
    ) -> bool:
        """
        Check Ollama server availability.
        """

        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(
                    f"{self.base_url}/api/tags",
                    timeout=5,
                )

                return (
                    response.status_code
                    == 200
                )


        except Exception:

            return False