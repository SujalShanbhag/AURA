from __future__ import annotations

import asyncio
import logging
import random
import time

from typing import AsyncIterator

from app.ai.models import (
    AIContext,
    AIResponse,
)

from app.ai.provider_registry import ProviderRegistry


logger = logging.getLogger(
    "aura.ai.orchestrator"
)


class Orchestrator:
    """
    Central AI execution engine.

    Handles:
    - Provider routing
    - Retry logic
    - Fallback
    - Streaming
    - Health monitoring
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        primary_provider: str,
        fallback_providers: list[str] | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        request_timeout: float = 120.0,
    ):
        self.registry = registry
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_timeout = request_timeout

    # =========================================================
    # Provider Chain
    # =========================================================

    def _provider_chain(self) -> list[str]:
        chain = [self.primary_provider]

        for provider in self.fallback_providers:
            if provider not in chain:
                chain.append(provider)

        return chain

    # =========================================================
    # Generate
    # =========================================================

    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:

        last_exception: Exception | None = None

        for provider_name in self._provider_chain():

            try:
                provider = self.registry.get(provider_name)

            except Exception as exc:
                last_exception = exc
                logger.warning(
                    "Provider '%s' unavailable.",
                    provider_name,
                )
                continue

            for attempt in range(1, self.max_retries + 1):

                start = time.perf_counter()

                try:

                    response = await asyncio.wait_for(
                        provider.generate(context),
                        timeout=self.request_timeout,
                    )

                    latency = (
                        time.perf_counter() - start
                    ) * 1000

                    response.provider.latency_ms = latency

                    logger.info(
                        "Generation successful.",
                        extra={
                            "provider": provider.name,
                            "attempt": attempt,
                            "latency_ms": latency,
                        },
                    )

                    return response

                except asyncio.TimeoutError as exc:

                    last_exception = exc

                    logger.warning(
                        "Provider '%s' timed out (attempt %d).",
                        provider_name,
                        attempt,
                    )

                except Exception as exc:

                    last_exception = exc

                    logger.warning(
                        "Provider '%s' failed (attempt %d): %s",
                        provider_name,
                        attempt,
                        exc,
                    )

                if attempt < self.max_retries:

                    delay = (
                        self.retry_delay
                        * (2 ** (attempt - 1))
                    ) + random.uniform(0, 0.5)

                    await asyncio.sleep(delay)

        raise RuntimeError(
            "All AI providers failed."
        ) from last_exception

    # =========================================================
    # Streaming
    # =========================================================

    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:

        last_exception: Exception | None = None

        for provider_name in self._provider_chain():

            try:
                provider = self.registry.get(provider_name)

            except Exception as exc:
                last_exception = exc
                continue

            if not provider.supports_streaming:
                continue

            try:

                stream = provider.stream(context)

                while True:

                    try:
                        chunk = await asyncio.wait_for(
                            anext(stream),
                            timeout=self.request_timeout,
                        )

                    except StopAsyncIteration:
                        break

                    if chunk:
                        yield chunk

                return

            except asyncio.TimeoutError as exc:

                last_exception = exc

                logger.warning(
                    "Streaming timed out for provider '%s'.",
                    provider_name,
                )

            except Exception as exc:

                last_exception = exc

                logger.warning(
                    "Streaming failed for provider '%s': %s",
                    provider_name,
                    exc,
                )

        raise RuntimeError(
            "No streaming provider available."
        ) from last_exception

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> dict[str, bool]:

        return await self.registry.health_check()