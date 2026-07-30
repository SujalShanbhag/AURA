from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import AsyncIterator

import httpx

from app.ai.models import (
    AIContext,
    AIProviderInfo,
    AIResponse,
    TokenUsage,
)
from app.ai.provider import AIProvider
from app.core.config import settings


logger = logging.getLogger(
    "aura.ai.providers.ollama"
)


class OllamaProvider(AIProvider):
    """
    Ollama local LLM provider.

    Supports:

    - Local inference
    - Streaming generation
    - Health monitoring
    """

    def __init__(
        self,
        model: str | None = None,
    ) -> None:

        self._model = model or settings.OLLAMA_MODEL

        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=120.0,
                write=30.0,
                pool=30.0,
            ),
        )

    # =========================================================
    # Provider Metadata
    # =========================================================

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model(self) -> str:
        return self._model

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_tools(self) -> bool:
        return False

    # =========================================================
    # Prompt Builder
    # =========================================================

    def _build_prompt(
        self,
        context: AIContext,
    ) -> str:

        parts: list[str] = []

        if context.system_prompt:
            parts.append(context.system_prompt)

        memories = context.metadata.get(
            "semantic_memory",
            [],
        )

        if memories:
            parts.append("\nRelevant memories:")

            for memory in memories:
                parts.append(f"- {memory}")

        history = context.metadata.get(
            "recent_history",
            [],
        )

        if history:
            parts.append("\nConversation history:")

            for item in history:

                if isinstance(item, dict):

                    role = item.get("role", "user")
                    message = item.get(
                        "message",
                        item.get("content", ""),
                    )

                    parts.append(
                        f"{role.capitalize()}: {message}"
                    )

                else:

                    parts.append(str(item))

        parts.append(f"\nUser: {context.message}")

        return "\n".join(parts)

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

            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": self._build_prompt(context),
                    "stream": False,
                },
            )

            response.raise_for_status()

            data = response.json()

            latency = (
                time.perf_counter() - start
            ) * 1000

            content = (
                data.get("response", "")
            ).strip()

            if not content:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

            prompt_tokens = data.get(
                "prompt_eval_count",
                0,
            )

            completion_tokens = data.get(
                "eval_count",
                0,
            )

            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=(
                    prompt_tokens
                    + completion_tokens
                ),
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
                finish_reason=(
                    "stop"
                    if data.get("done")
                    else None
                ),
                metadata={
                    "local": True,
                    "base_url": self.base_url,
                    "request_id": str(
                        context.request_id
                    ),
                },
                created_at=datetime.now(
                    timezone.utc
                ),
            )

        except Exception as exc:

            logger.exception(
                "Ollama generation failed."
            )

            raise RuntimeError(
                "Ollama provider failed."
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

            async with self.client.stream(
                "POST",
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": self._build_prompt(
                        context
                    ),
                    "stream": True,
                },
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line:
                        continue

                    try:
                        data = json.loads(line)

                    except json.JSONDecodeError:
                        continue

                    text = data.get("response")

                    if text:
                        yield text

                    if data.get("done", False):
                        break

        except Exception as exc:

            logger.exception(
                "Ollama streaming failed."
            )

            raise RuntimeError(
                "Ollama streaming failed."
            ) from exc

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:

        try:

            response = await self.client.get(
                "/api/tags",
                timeout=5.0,
            )

            response.raise_for_status()

            models = response.json().get(
                "models",
                [],
            )

            available = {
                model.get("name", "")
                for model in models
            }

            return any(
                name.startswith(self.model)
                for name in available
            )

        except Exception:

            logger.exception(
                "Ollama health check failed."
            )

            return False

    # =========================================================
    # Cleanup
    # =========================================================

    async def close(
        self,
    ) -> None:

        await self.client.aclose()