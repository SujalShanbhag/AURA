from __future__ import annotations

from typing import Dict

from app.ai.provider import AIProvider


class ProviderRegistry:
    """
    Registry for AI model providers.

    The orchestrator interacts only with this registry.
    Providers can be added or removed without changing
    the AI execution pipeline.
    """

    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}


    def register(
        self,
        provider: AIProvider,
    ) -> None:
        """
        Register an AI provider.
        """

        self._providers[
            provider.name
        ] = provider


    def get(
        self,
        name: str,
    ) -> AIProvider:
        """
        Retrieve provider by name.
        """

        provider = self._providers.get(
            name
        )

        if provider is None:
            raise ValueError(
                f"AI provider '{name}' not registered."
            )

        return provider


    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove provider.
        """

        self._providers.pop(
            name,
            None,
        )


    def list_providers(
        self,
    ) -> list[str]:
        """
        Return available providers.
        """

        return list(
            self._providers.keys()
        )


    async def health_check(
        self,
    ) -> dict[str, bool]:
        """
        Check provider availability.
        """

        result: dict[str, bool] = {}

        for name, provider in self._providers.items():

            result[name] = (
                await provider.health_check()
            )

        return result