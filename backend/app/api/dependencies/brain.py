from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.brain import AuraBrain
from app.ai.container import get_ai_container
from app.core.database import get_db
from app.memory.memory_service import MemoryService


async def get_aura_brain(
    db: AsyncSession = Depends(get_db),
) -> AuraBrain:
    """
    Creates AuraBrain for each request.
    """

    container = get_ai_container()

    memory = MemoryService(
        db=db,
        embedding_service=container.embedding_service,
        qdrant_memory=container.qdrant_memory,
    )

    return AuraBrain(
        orchestrator=container.orchestrator,
        memory=memory,
    )