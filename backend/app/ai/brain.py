from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone
from uuid import UUID

from app.ai.models import AIContext
from app.ai.models import AIResponse
from app.ai.orchestrator import Orchestrator


logger = logging.getLogger(
    "aura.ai.brain"
)


class AuraBrain:
    """
    Central intelligence layer of AURA.

    Responsibilities:
    - Prepare AI context
    - Manage conversation execution
    - Coordinate AI orchestration
    - Return normalized responses

    Future integrations:
    - Memory engine
    - Emotion engine
    - Vision
    - Voice
    - Personalization
    """

    def __init__(
        self,
        orchestrator: Orchestrator,
    ):
        self.orchestrator = orchestrator


    async def chat(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> AIResponse:
        """
        Process a user message.
        """

        context = AIContext(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            metadata=metadata or {},
            timestamp=datetime.now(
                timezone.utc
            ),
        )

        logger.info(
            "Processing user message",
            extra={
                "user_id": str(user_id),
                "conversation_id": (
                    str(conversation_id)
                    if conversation_id
                    else None
                ),
            },
        )

        response = await self.orchestrator.generate(
            context
        )

        return response


    async def stream_chat(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: UUID | None = None,
        metadata: dict | None = None,
    ):
        """
        Streaming chat response.
        """

        context = AIContext(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            metadata=metadata or {},
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
    ) -> dict:
        """
        Check AI subsystem status.
        """

        return await self.orchestrator.health_check()