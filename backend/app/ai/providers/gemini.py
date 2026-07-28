from __future__ import annotations

import time
import logging
from datetime import datetime
from datetime import timezone
from typing import AsyncIterator

from google import genai

from app.ai.models import AIContext
from app.ai.models import AIProviderInfo
from app.ai.models import AIResponse
from app.ai.models import TokenUsage
from app.ai.provider import AIProvider
from app.core.config import settings


logger = logging.getLogger(
    "aura.ai.gemini"
)


class GeminiProvider(AIProvider):
    """
    Google Gemini AI provider.

    Implements:
    - Text generation
    - Streaming
    - Health checks
    """


    name = "gemini"


    def __init__(
        self,
        model: str | None = None,
    ):
        self.model = (
            model
            or settings.GEMINI_MODEL
        )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )


    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Generate complete response.
        """

        start = time.perf_counter()

        try:

            response = (
                await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=context.message,
                )
            )

            latency = (
                time.perf_counter()
                - start
            ) * 1000


            return AIResponse(
                content=response.text,

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
                "Gemini generation failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "Gemini provider failed."
            ) from exc



    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:
        """
        Stream Gemini response.
        """

        try:

            response = (
                await self.client.aio.models.generate_content_stream(
                    model=self.model,
                    contents=context.message,
                )
            )


            async for chunk in response:

                if chunk.text:

                    yield chunk.text


        except Exception as exc:

            logger.exception(
                "Gemini streaming failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "Gemini streaming failed."
            ) from exc



    async def health_check(
        self,
    ) -> bool:
        """
        Verify Gemini availability.
        """

        try:

            await self.client.aio.models.generate_content(
                model=self.model,
                contents="Health check",
            )

            return True


        except Exception:

            return False