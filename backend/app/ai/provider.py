from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.ai.models import AIContext
from app.ai.models import AIResponse


class AIProvider(ABC):
    """
    Abstract base class for all AI providers.

    Every provider (OpenAI, Gemini, Anthropic, Ollama, etc.)
    must implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable provider name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model(self) -> str:
        """
        Active model name.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Generate a complete response.
        """
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        context: AIContext,
    ):
        """
        Stream tokens from the provider.

        Returns an async iterator.
        """
        raise NotImplementedError

    async def health_check(self) -> bool:
        """
        Optional provider health check.
        """

        return True