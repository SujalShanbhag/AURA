from __future__ import annotations

from app.ai.emotion import EmotionEngine
from app.ai.models import (
    AIContext,
    ChatMessage,
    MemoryItem,
    UserProfile,
)
from app.ai.personality import PersonalityEngine


class ContextBuilder:
    """
    Builds the complete AI context used for every request.

    External providers (Redis, PostgreSQL, Qdrant, etc.) are injected
    through setter methods so this class remains independent of any
    storage implementation.
    """

    def __init__(
        self,
        personality: PersonalityEngine,
        emotion: EmotionEngine,
    ):
        self.personality = personality
        self.emotion = emotion

        self._memory_provider = None
        self._profile_provider = None

    def set_memory_provider(self, provider) -> None:
        self._memory_provider = provider

    def set_profile_provider(self, provider) -> None:
        self._profile_provider = provider

    async def build(
        self,
        *,
        user_profile: UserProfile,
        message: str,
        conversation: list[ChatMessage],
    ) -> AIContext:
        """
        Build the complete context for one AI request.
        """

        emotion_result = self.emotion.detect(message)

        personality_prompt = (
            self.personality.build_system_prompt()
        )

        emotion_prompt = (
            self.emotion.response_guidance(
                emotion_result
            )
        )

        system_prompt = (
            f"{personality_prompt}\n\n"
            f"{emotion_prompt}"
        )

        memories: list[MemoryItem] = []

        if self._memory_provider is not None:
            memories = await self._memory_provider.search(
                user_id=user_profile.user_id,
                query=message,
                limit=10,
            )

        return AIContext(
            system_prompt=system_prompt,
            profile=user_profile,
            memories=memories,
            conversation=conversation,
            metadata={
                "emotion": emotion_result.emotion.value,
                "emotion_confidence": emotion_result.confidence,
            },
        )