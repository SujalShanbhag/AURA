from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

from app.ai.provider import AIProvider


logger = logging.getLogger("aura.ai.provider_registry")


class ProviderRegistry:
    """
    Registry for AI providers.

    Responsibilities:
    - Provider registration
    - Provider lookup
    - Health monitoring
    - Lifecycle management
    """

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}

    # ==========================================================
    # Registration
    # ==========================================================

    def register(
        self,
        provider: AIProvider,
        *,
        replace: bool = False,
    ) -> None:
        name = provider.name.lower()

        if name in self._providers and not replace:
            raise ValueError(
                f"Provider '{name}' is already registered."
            )

        self._providers[name] = provider

        logger.info(
            "Registered AI provider '%s' (%s)",
            name,
            provider.model,
        )

    def register_many(
        self,
        providers: Iterable[AIProvider],
    ) -> None:
        for provider in providers:
            self.register(provider)

    # ==========================================================
    # Retrieval
    # ==========================================================

    def get(
        self,
        name: str,
    ) -> AIProvider:
        provider = self._providers.get(name.lower())

        if provider is None:
            raise ValueError(
                f"Provider '{name}' is not registered."
            )

        return provider

    def has(
        self,
        name: str,
    ) -> bool:
        return name.lower() in self._providers

    # ==========================================================
    # Removal
    # ==========================================================

    async def remove(
        self,
        name: str,
    ) -> bool:
        provider = self._providers.pop(
            name.lower(),
            None,
        )

        if provider is None:
            return False

        try:
            await provider.close()

        except Exception:
            logger.exception(
                "Failed closing provider '%s'.",
                name,
            )

        logger.info(
            "Removed provider '%s'.",
            name,
        )

        return True

    async def clear(self) -> None:
        await self.shutdown()

    # ==========================================================
    # Information
    # ==========================================================

    def list_providers(self) -> tuple[str, ...]:
        return tuple(self._providers.keys())

    def count(self) -> int:
        return len(self._providers)

    def metadata(self) -> dict[str, dict]:
        return {
            name: {
                "model": provider.model,
                "streaming": provider.supports_streaming,
                "tools": provider.supports_tools,
            }
            for name, provider in self._providers.items()
        }

    # ==========================================================
    # Health Monitoring
    # ==========================================================

    async def health_check(
        self,
    ) -> dict[str, bool]:

        async def check(
            name: str,
            provider: AIProvider,
        ) -> tuple[str, bool]:
            try:
                healthy = await provider.health_check()
                return name, healthy

            except Exception:
                logger.exception(
                    "Health check failed for provider '%s'.",
                    name,
                )
                return name, False

        results = await asyncio.gather(
            *(
                check(name, provider)
                for name, provider in self._providers.items()
            )
        )

        return dict(results)

    # ==========================================================
    # Shutdown
    # ==========================================================

    async def shutdown(self) -> None:
        """
        Gracefully shut down all registered providers.
        """

        async def close_provider(
            name: str,
            provider: AIProvider,
        ) -> None:
            try:
                await provider.close()

            except Exception:
                logger.exception(
                    "Failed shutting down provider '%s'.",
                    name,
                )

        await asyncio.gather(
            *(
                close_provider(name, provider)
                for name, provider in self._providers.items()
            ),
            return_exceptions=True,
        )

        self._providers.clear()

        logger.info(
            "Provider registry shutdown completed."
        )