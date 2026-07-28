from __future__ import annotations

import logging
import time
from datetime import datetime
from datetime import timezone
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.ai.models import AIContext
from app.ai.models import AIProviderInfo
from app.ai.models import AIResponse
from app.ai.models import TokenUsage
from app.ai.provider import AIProvider
from app.core.config import settings


logger = logging.getLogger(
    "aura.ai.openai"
)


class OpenAIProvider(AIProvider):
    """
    OpenAI provider implementation.

    Supports:
    - Chat generation
    - Streaming
    - Health checks
    """

    name = "openai"


    def __init__(
        self,
        model: str | None = None,
    ):
        self.model = (
            model
            or settings.OPENAI_MODEL
        )

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )


    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Generate a complete response.
        """

        start = time.perf_counter()

        try:

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            context.system_prompt
                            or "You are AURA, an AI companion."
                        ),
                    },
                    {
                        "role": "user",
                        "content": context.message,
                    },
                ],
            )

            latency = (
                time.perf_counter()
                - start
            ) * 1000


            message = (
                response.choices[0]
                .message.content
                or ""
            )

            usage = TokenUsage()

            if response.usage:

                usage = TokenUsage(
                    input_tokens=(
                        response.usage.prompt_tokens
                    ),
                    output_tokens=(
                        response.usage.completion_tokens
                    ),
                    total_tokens=(
                        response.usage.total_tokens
                    ),
                )


            return AIResponse(
                content=message,

                provider=AIProviderInfo(
                    name=self.name,
                    model=self.model,
                    latency_ms=latency,
                ),

                usage=usage,

                finish_reason=(
                    response.choices[0]
                    .finish_reason
                ),

                created_at=datetime.now(
                    timezone.utc
                ),
            )


        except Exception as exc:

            logger.exception(
                "OpenAI generation failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "OpenAI provider failed."
            ) from exc



    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:
        """
        Stream OpenAI response.
        """

        try:

            stream = await self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            context.system_prompt
                            or "You are AURA, an AI companion."
                        ),
                    },
                    {
                        "role": "user",
                        "content": context.message,
                    },
                ],

                stream=True,
            )


            async for chunk in stream:

                content = (
                    chunk.choices[0]
                    .delta.content
                )

                if content:

                    yield content


        except Exception as exc:

            logger.exception(
                "OpenAI streaming failed",
                exc_info=exc,
            )

            raise RuntimeError(
                "OpenAI streaming failed."
            ) from exc



    async def health_check(
        self,
    ) -> bool:
        """
        Check OpenAI availability.
        """

        try:

            await self.client.models.list()

            return True


        except Exception:

            return False