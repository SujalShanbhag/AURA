from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.brain import AuraBrain
from app.ai.container import AIContainer
from app.ai.container import get_ai_container
from app.core.database import get_db
from app.memory.memory_service import MemoryService


# ============================================================
# Infrastructure
# ============================================================

def get_container() -> AIContainer:
    """
    Return the singleton AI infrastructure container.

    This provides access to:

    - AI Orchestrator
    - Embedding Service
    - Redis
    - Qdrant
    """

    return get_ai_container()


# ============================================================
# Memory Service
# ============================================================

async def get_memory_service(
    db: AsyncSession = Depends(get_db),
    container: AIContainer = Depends(get_container),
) -> MemoryService:
    """
    Create a request-scoped MemoryService.

    Responsible for:

    - PostgreSQL memory
    - Embedding generation
    - Qdrant synchronization
    """

    return MemoryService(
        db=db,
        embedding_service=container.embedding_service,
        qdrant_memory=container.qdrant_memory,
    )


# ============================================================
# Aura Brain
# ============================================================

async def get_aura_brain(
    memory_service: MemoryService = Depends(get_memory_service),
    container: AIContainer = Depends(get_container),
) -> AuraBrain:
    """
    Create a request-scoped AuraBrain.

    Provides:

    - AI orchestration
    - Conversation memory
    - Semantic memory
    """

    return AuraBrain(
        orchestrator=container.orchestrator,
        memory=memory_service,
    )