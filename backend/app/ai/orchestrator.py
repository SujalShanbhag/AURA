from __future__ import annotations

import asyncio
import logging
import time
from typing import AsyncIterator

from app.ai.models import AIContext
from app.ai.models import AIResponse
from app.ai.provider_registry import ProviderRegistry


logger = logging.getLogger(
    "aura.ai.orchestrator"
)


class Orchestrator:
    """
    Production AI execution engine.

    Responsibilities:
    - Provider routing
    - Retry handling
    - Fallback execution
    - Streaming support
    - Error normalization
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        primary_provider: str,
        fallback_providers: list[str] | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.registry = registry

        self.primary_provider = (
            primary_provider
        )

        self.fallback_providers = (
            fallback_providers or []
        )

        self.max_retries = max_retries

        self.retry_delay = retry_delay


    def _provider_chain(
        self,
    ) -> list[str]:
        """
        Return providers in execution order.
        """

        return [
            self.primary_provider,
            *self.fallback_providers,
        ]


    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Execute AI generation.

        Tries primary provider first,
        then fallback providers.
        """

        providers = self._provider_chain()

        errors: list[str] = []

        for provider_name in providers:

            provider = self.registry.get(
                provider_name
            )

            for attempt in range(
                self.max_retries
            ):

                start = time.perf_counter()

                try:

                    response = await provider.generate(
                        context
                    )

                    elapsed = (
                        time.perf_counter()
                        - start
                    )

                    logger.info(
                        "AI generation completed",
                        extra={
                            "provider": provider.name,
                            "model": provider.model,
                            "duration": elapsed,
                        },
                    )

                    return response


                except Exception as exc:

                    errors.append(
                        f"{provider_name}: {exc}"
                    )

                    logger.warning(
                        "AI provider failed",
                        extra={
                            "provider": provider_name,
                            "attempt": attempt + 1,
                            "error": str(exc),
                        },
                    )

                    if attempt < (
                        self.max_retries - 1
                    ):
                        await asyncio.sleep(
                            self.retry_delay
                            * (
                                attempt + 1
                            )
                        )


        raise RuntimeError(
            "All AI providers failed: "
            + " | ".join(errors)
        )


    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:
        """
        Stream AI response tokens.
        """

        providers = self._provider_chain()

        for provider_name in providers:

            provider = self.registry.get(
                provider_name
            )

            try:

                async for chunk in provider.stream(
                    context
                ):
                    yield chunk

                return


            except Exception as exc:

                logger.warning(
                    "Streaming provider failed",
                    extra={
                        "provider": provider_name,
                        "error": str(exc),
                    },
                )

                continue


        raise RuntimeError(
            "No streaming provider available."
        )


    async def health_check(
        self,
    ) -> dict[str, bool]:
        """
        Return AI provider health status.
        """

        return await self.registry.health_check()