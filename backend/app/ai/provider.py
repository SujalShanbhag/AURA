from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import AsyncIterator

from app.ai.models import AIContext
from app.ai.models import AIResponse


class AIProvider(ABC):
    """
    Abstract AI provider interface.

    Every AI provider used by AURA
    must implement this contract.

    Examples:
    - Gemini
    - OpenAI
    - Ollama
    - Future local models
    """


    name: str

    model: str


    @abstractmethod
    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:
        """
        Generate a complete AI response.
        """

        pass


    @abstractmethod
    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:
        """
        Stream response chunks.

        Used for:
        - Chat streaming
        - Voice interaction
        - Real-time UI
        """

        pass


    @abstractmethod
    async def health_check(
        self,
    ) -> bool:
        """
        Check provider availability.
        """

        pass