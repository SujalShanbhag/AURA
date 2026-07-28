from __future__ import annotations

from functools import lru_cache

from app.ai.brain import AuraBrain
from app.ai.orchestrator import Orchestrator
from app.ai.provider_registry import ProviderRegistry
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.ollama import OllamaProvider
from app.core.config import settings


class AIContainer:
    """
    Production AI dependency container.

    Creates and manages:

    - Provider Registry
    - AI Providers
    - Orchestrator
    - AURA Brain
    """

    def __init__(self):

        self.registry = (
            ProviderRegistry()
        )

        self._register_providers()

        self.orchestrator = Orchestrator(
            registry=self.registry,
            primary_provider=(
                settings.AI_PRIMARY_PROVIDER
            ),
            fallback_providers=(
                settings.AI_FALLBACK_PROVIDERS
            ),
            max_retries=(
                settings.AI_MAX_RETRIES
            ),
        )

        self.brain = AuraBrain(
            orchestrator=self.orchestrator
        )


    def _register_providers(
        self,
    ):
        """
        Register available AI providers.
        """

        self.registry.register(
            GeminiProvider()
        )

        self.registry.register(
            OpenAIProvider()
        )

        self.registry.register(
            OllamaProvider()
        )


    def get_brain(
        self,
    ) -> AuraBrain:
        """
        Return AURA intelligence instance.
        """

        return self.brain


@lru_cache
def get_ai_container() -> AIContainer:
    """
    Singleton AI container.

    Prevents recreating AI clients
    for every request.
    """

    return AIContainer()


def get_aura_brain() -> AuraBrain:
    """
    FastAPI dependency.
    """

    return (
        get_ai_container()
        .get_brain()
    )