from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone
from uuid import UUID

from app.ai.models import AIContext
from app.ai.models import AIResponse
from app.ai.orchestrator import Orchestrator
from app.memory.manager import MemoryManager


logger = logging.getLogger(
    "aura.ai.brain"
)


class AuraBrain:
    """
    Central intelligence layer of AURA.

    Responsibilities:

    - Manage conversations
    - Retrieve memories
    - Build AI context
    - Execute AI generation
    - Store new memories

    Future integrations:

    - Emotion engine
    - Voice engine
    - Vision engine
    - Personality engine
    """


    def __init__(
        self,
        orchestrator: Orchestrator,
        memory: MemoryManager,
    ):

        self.orchestrator = orchestrator

        self.memory = memory



    async def chat(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: UUID,
        metadata: dict | None = None,
    ) -> AIResponse:
        """
        Process user conversation.
        """


        # -------------------------------------------------
        # 1. Store user message
        # -------------------------------------------------

        await self.memory.remember_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            role="user",
            message=message,
            metadata=metadata,
        )


        # -------------------------------------------------
        # 2. Retrieve recent context
        # -------------------------------------------------

        recent_context = (
            await self.memory.get_recent_context(
                user_id=user_id,
                conversation_id=conversation_id,
            )
        )


        # -------------------------------------------------
        # 3. Retrieve long-term memories
        # -------------------------------------------------

        long_term = (
            await self.memory.get_long_term_memory(
                user_id=user_id,
            )
        )


        memory_context = {
            "recent": recent_context,
            "long_term": [
                item.content
                for item in long_term
            ],
        }



        # -------------------------------------------------
        # 4. Build AI context
        # -------------------------------------------------

        context = AIContext(
            user_id=user_id,

            conversation_id=conversation_id,

            message=message,

            system_prompt=(
                "You are AURA, a personal AI companion. "
                "Use available memory to personalize responses."
            ),

            metadata={
                "memory": memory_context,
                **(
                    metadata or {}
                ),
            },

            timestamp=datetime.now(
                timezone.utc
            ),
        )


        # -------------------------------------------------
        # 5. Generate response
        # -------------------------------------------------

        response = await self.orchestrator.generate(
            context
        )


        # -------------------------------------------------
        # 6. Store AI response
        # -------------------------------------------------

        await self.memory.remember_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            message=response.content,
            metadata={
                "provider": (
                    response.provider.name
                ),

                "model": (
                    response.provider.model
                ),
            },
        )


        logger.info(
            "Conversation completed",
            extra={
                "user_id": str(user_id),
                "conversation_id": str(
                    conversation_id
                ),
            },
        )


        return response



    async def stream_chat(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: UUID,
    ):
        """
        Streaming chat.

        Memory storage is handled after
        streaming integration is added.
        """

        context = AIContext(
            user_id=user_id,

            conversation_id=conversation_id,

            message=message,

            timestamp=datetime.now(
                timezone.utc
            ),
        )


        async for chunk in self.orchestrator.stream(
            context
        ):
            yield chunk



    async def health_check(
        self,
    ):
        """
        Check AI providers.
        """

        return await self.orchestrator.health_check()