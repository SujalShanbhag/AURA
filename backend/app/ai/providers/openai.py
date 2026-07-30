from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.ai.models import (
    AIContext,
    AIProviderInfo,
    AIResponse,
    TokenUsage,
)
from app.ai.provider import AIProvider
from app.core.config import settings


logger = logging.getLogger(
    "aura.ai.providers.openai"
)


class OpenAIProvider(AIProvider):
    """
    OpenAI Provider.

    Supports:

    - Chat Completions
    - Streaming
    - Token usage tracking
    - Health monitoring
    """

    def __init__(
        self,
        model: str | None = None,
    ) -> None:

        self._model = model or settings.OPENAI_MODEL

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    # =========================================================
    # Provider Metadata
    # =========================================================

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_tools(self) -> bool:
        return True

    # =========================================================
    # Message Builder
    # =========================================================

    def _messages(
        self,
        context: AIContext,
    ) -> list[dict[str, Any]]:

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    context.system_prompt
                    or "You are AURA, a helpful AI companion."
                ),
            }
        ]

        semantic_memory = context.metadata.get(
            "semantic_memory",
            [],
        )

        if semantic_memory:

            memory_text = "\n".join(
                f"- {str(memory)}"
                for memory in semantic_memory
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Relevant memories:\n"
                        f"{memory_text}"
                    ),
                }
            )

        history = context.metadata.get(
            "recent_history",
            [],
        )

        for item in history:

            if isinstance(item, dict):

                role = item.get(
                    "role",
                    "user",
                )

                content = item.get(
                    "message",
                    item.get("content", ""),
                )

            else:

                role = "user"
                content = str(item)

            if content:

                messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": context.message,
            }
        )

        return messages

    # =========================================================
    # Generate
    # =========================================================

    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:

        await self.validate_context(context)

        start = time.perf_counter()

        try:

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self._messages(context),
            )

            latency = (
                time.perf_counter() - start
            ) * 1000

            if not response.choices:

                raise RuntimeError(
                    "OpenAI returned no choices."
                )

            choice = response.choices[0]

            content = (
                choice.message.content or ""
            ).strip()

            if not content:

                raise RuntimeError(
                    "OpenAI returned an empty response."
                )

            usage = TokenUsage()

            if response.usage:

                usage = TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )

            return AIResponse(
                content=content,
                provider=AIProviderInfo(
                    name=self.name,
                    model=self.model,
                    latency_ms=latency,
                    supports_streaming=self.supports_streaming,
                    supports_tools=self.supports_tools,
                ),
                usage=usage,
                finish_reason=choice.finish_reason,
                metadata={
                    "request_id": str(
                        context.request_id
                    )
                },
                created_at=datetime.now(
                    timezone.utc
                ),
            )

        except Exception as exc:

            logger.exception(
                "OpenAI generation failed."
            )

            raise RuntimeError(
                "OpenAI provider failed."
            ) from exc

    # =========================================================
    # Streaming
    # =========================================================

    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:

        await self.validate_context(context)

        try:

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=self._messages(context),
                stream=True,
            )

            async for chunk in stream:

                if not chunk.choices:
                    continue

                delta = (
                    chunk.choices[0]
                    .delta
                    .content
                )

                if delta:
                    yield delta

        except Exception as exc:

            logger.exception(
                "OpenAI streaming failed."
            )

            raise RuntimeError(
                "OpenAI streaming failed."
            ) from exc

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:

        try:

            await self.client.models.list()

            return True

        except Exception:

            logger.exception(
                "OpenAI health check failed."
            )

            return False

    # =========================================================
    # Cleanup
    # =========================================================

    async def close(
        self,
    ) -> None:

        await self.client.close()