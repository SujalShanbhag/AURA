from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncIterator

from app.ai.models import (
    AIContext,
    AIResponse,
)


class AIProvider(ABC):
    """
    Base interface for every AI provider.

    Implemented by:
    - Gemini
    - OpenAI
    - Ollama
    - Anthropic
    - Local models
    """

    # ==========================================================
    # Identity
    # ==========================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique provider identifier.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model(self) -> str:
        """
        Active model name.
        """
        raise NotImplementedError

    # ==========================================================
    # Capabilities
    # ==========================================================

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_tools(self) -> bool:
        return False

    @property
    def max_context_tokens(self) -> int | None:
        return None

    @property
    def default_timeout(self) -> float:
        return 120.0

    # ==========================================================
    # Validation
    # ==========================================================

    async def validate_context(
        self,
        context: AIContext,
    ) -> None:
        """
        Validate an AI request before sending it to the provider.
        """

        if context is None:
            raise ValueError("AI context is required.")

        if not isinstance(context.message, str):
            raise ValueError("Message must be a string.")

        if not context.message.strip():
            raise ValueError("Message cannot be empty.")

    # ==========================================================
    # Generation
    # ==========================================================

    @abstractmethod
    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Generate a complete AI response.
        """
        raise NotImplementedError

    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:
        """
        Default streaming implementation.

        Providers that support native streaming should override
        this method.
        """

        await self.validate_context(context)

        response = await self.generate(context)

        if response.content:
            yield response.content

    # ==========================================================
    # Health
    # ==========================================================

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check whether the provider is available.
        """
        raise NotImplementedError

    # ==========================================================
    # Lifecycle
    # ==========================================================

    async def close(self) -> None:
        """
        Release provider resources.

        Override if the provider maintains network clients,
        sockets, or background tasks.
        """
        return None