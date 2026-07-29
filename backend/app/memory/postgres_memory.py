from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.models import ConversationMemory
from app.memory.models import MemoryType
from app.models.memory import Memory


class PostgresMemory:
    """
    PostgreSQL memory repository.

    Responsible only for database operations.

    It does NOT:

    - Generate embeddings
    - Communicate with Redis
    - Communicate with Qdrant
    - Contain business logic
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def save_conversation(
        self,
        memory: ConversationMemory,
    ) -> Memory:

        record = Memory(
            user_id=memory.user_id,
            conversation_id=memory.conversation_id,
            memory_type=MemoryType.CONVERSATION.value,
            role=memory.role,
            content=memory.message,
            metadata_json=memory.metadata,
            created_at=memory.created_at,
        )

        self.db.add(record)

        await self.db.flush()
        await self.db.refresh(record)

        return record

    async def save_user_memory(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ) -> Memory:

        record = Memory(
            user_id=user_id,
            memory_type=MemoryType.LONG_TERM.value,
            content=content,
            importance=importance,
            metadata_json=metadata or {},
        )

        self.db.add(record)

        await self.db.flush()
        await self.db.refresh(record)

        return record

    async def get_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 100,
    ) -> list[Memory]:

        result = await self.db.execute(
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.conversation_id == conversation_id,
            )
            .order_by(Memory.created_at.asc())
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_user_memories(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ) -> list[Memory]:

        result = await self.db.execute(
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.memory_type == MemoryType.LONG_TERM.value,
            )
            .order_by(
                Memory.importance.desc(),
                Memory.created_at.desc(),
            )
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_memory(
        self,
        memory_id: UUID,
    ) -> Memory | None:

        result = await self.db.execute(
            select(Memory).where(
                Memory.id == memory_id
            )
        )

        return result.scalar_one_or_none()

    async def update_qdrant_point(
        self,
        *,
        memory: Memory,
        point_id: str,
    ) -> Memory:

        memory.qdrant_point_id = point_id

        await self.db.flush()
        await self.db.refresh(memory)

        return memory

    async def delete_memory(
        self,
        memory_id: UUID,
    ) -> None:

        await self.db.execute(
            delete(Memory).where(
                Memory.id == memory_id
            )
        )

        await self.db.flush()