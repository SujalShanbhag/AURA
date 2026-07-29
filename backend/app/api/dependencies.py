from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.brain import AuraBrain
from app.ai.container import get_ai_container
from app.core.database import AsyncSessionLocal
from app.memory.memory_service import MemoryService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for each request.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_memory_service(
    db: AsyncSession = Depends(get_db),
) -> MemoryService:
    """
    Create a request-scoped MemoryService.
    """

    container = get_ai_container()

    return MemoryService(
        db=db,
        embedding_service=container.embedding_service,
        qdrant_memory=container.qdrant_memory,
    )


async def get_aura_brain(
    memory_service: MemoryService = Depends(get_memory_service),
) -> AuraBrain:
    """
    Create a request-scoped AuraBrain.
    """

    container = get_ai_container()

    return AuraBrain(
        orchestrator=container.orchestrator,
        memory=memory_service,
    )