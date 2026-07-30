from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from uuid import UUID

from app.ai.models import AIContext, AIResponse
from app.ai.orchestrator import Orchestrator
from app.memory.memory_service import MemoryService
from app.memory.models import ConversationMemory


logger = logging.getLogger(
    "aura.ai.brain"
)


SYSTEM_PROMPT = (
    "You are AURA, a helpful personal AI companion. "
    "Use conversation history and stored memories "
    "to provide personalized, natural, and accurate responses."
)


class AuraBrain:
    """
    Main intelligence layer.

    Responsibilities:
    - Retrieve memories
    - Build AI context
    - Call AI providers
    - Store conversations
    - Store long-term memories
    """

    def __init__(
        self,
        *,
        orchestrator: Orchestrator,
        memory: MemoryService,
    ) -> None:

        self.orchestrator = orchestrator
        self.memory = memory

    # ==========================================================
    # Chat
    # ==========================================================

    async def chat(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> AIResponse:
        """
        Execute one AI conversation turn.
        """

        message = message.strip()

        if not message:
            raise ValueError(
                "Message cannot be empty."
            )

        metadata = metadata or {}

        try:

            # --------------------------------------------------
            # Store user message
            # --------------------------------------------------

            await self.memory.save_conversation(
                ConversationMemory(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    role="user",
                    message=message,
                    metadata=metadata,
                )
            )

            # --------------------------------------------------
            # Conversation history
            # --------------------------------------------------

            history = await self.memory.conversation_history(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=20,
            )

            history_text: list[str] = []

            for item in history:
                if hasattr(item, "message"):
                    history_text.append(item.message)
                else:
                    history_text.append(str(item))

            # --------------------------------------------------
            # Semantic memories
            # --------------------------------------------------

            semantic_results = await self.memory.semantic_search(
                user_id=user_id,
                query=message,
                limit=5,
            )

            semantic_memory = [
                item.content
                for item in semantic_results
            ]

            # --------------------------------------------------
            # Build AI context
            # --------------------------------------------------

            context = AIContext(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message,
                system_prompt=SYSTEM_PROMPT,
                metadata={
                    **metadata,
                    "recent_history": history_text,
                    "semantic_memory": semantic_memory,
                },
                timestamp=datetime.now(
                    timezone.utc
                ),
            )

            # --------------------------------------------------
            # Generate response
            # --------------------------------------------------

            response = await self.orchestrator.generate(
                context
            )

            # --------------------------------------------------
            # Store assistant message
            # --------------------------------------------------

            await self.memory.save_conversation(
                ConversationMemory(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    role="assistant",
                    message=response.content,
                    metadata={
                        "provider": response.provider.name,
                        "model": response.provider.model,
                    },
                )
            )

            return response

        except Exception as exc:

            logger.exception(
                "AURA chat failed."
            )

            raise RuntimeError(
                "Failed to process AI request."
            ) from exc

    # ==========================================================
    # Long-Term Memory
    # ==========================================================

    async def remember(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Store long-term memory.
        """

        return await self.memory.save_long_term_memory(
            user_id=user_id,
            content=content,
            importance=importance,
            metadata=metadata or {},
        )

    # ==========================================================
    # Streaming Chat
    # ==========================================================

    async def stream_chat(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream AI response.
        """

        message = message.strip()

        if not message:
            raise ValueError(
                "Message cannot be empty."
            )

        metadata = metadata or {}

        await self.memory.save_conversation(
            ConversationMemory(
                user_id=user_id,
                conversation_id=conversation_id,
                role="user",
                message=message,
                metadata=metadata,
            )
        )

        history = await self.memory.conversation_history(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=20,
        )

        history_text = [
            item.message if hasattr(item, "message") else str(item)
            for item in history
        ]

        semantic_results = await self.memory.semantic_search(
            user_id=user_id,
            query=message,
            limit=5,
        )

        semantic_memory = [
            item.content
            for item in semantic_results
        ]

        context = AIContext(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            system_prompt=SYSTEM_PROMPT,
            metadata={
                **metadata,
                "recent_history": history_text,
                "semantic_memory": semantic_memory,
            },
        )

        full_response = ""

        async for chunk in self.orchestrator.stream(
            context
        ):
            full_response += chunk
            yield chunk

        await self.memory.save_conversation(
            ConversationMemory(
                user_id=user_id,
                conversation_id=conversation_id,
                role="assistant",
                message=full_response,
                metadata={
                    "streamed": True,
                },
            )
        )

    # ==========================================================
    # Health
    # ==========================================================

    async def health_check(
        self,
    ) -> dict[str, bool]:
        """
        Check AI provider health.
        """

        try:
            return await self.orchestrator.health_check()

        except Exception:

            logger.exception(
                "AURA health check failed."
            )

            return {}