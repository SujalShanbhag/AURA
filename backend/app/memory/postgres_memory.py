from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.models import ConversationMemory, MemoryType
from app.models.memory import Memory


logger = logging.getLogger("aura.memory.postgres")


class PostgresMemory:
    """
    PostgreSQL memory repository.

    Responsible only for database persistence.

    Transaction ownership belongs to MemoryService.
    """

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    # =========================================================
    # Conversation Memory
    # =========================================================

    async def save_conversation(
        self,
        memory: ConversationMemory,
    ) -> Memory:
        """
        Save one conversation message.
        """

        record = Memory(
            user_id=memory.user_id,
            conversation_id=memory.conversation_id,
            memory_type=MemoryType.CONVERSATION.value,
            role=memory.role,
            content=memory.message,  # FIXED
            metadata_json=memory.metadata,
            created_at=memory.created_at,
        )

        try:
            self.db.add(record)

            await self.db.flush()
            await self.db.refresh(record)

            return record

        except Exception:
            logger.exception("Failed to save conversation.")
            raise

    # =========================================================
    # Long-Term Memory
    # =========================================================

    async def save_user_memory(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ) -> Memory:
        """
        Save a long-term memory.
        """

        record = Memory(
            user_id=user_id,
            memory_type=MemoryType.LONG_TERM.value,
            content=content,
            importance=importance,
            metadata_json=metadata or {},
        )

        try:
            self.db.add(record)

            await self.db.flush()
            await self.db.refresh(record)

            return record

        except Exception:
            logger.exception("Failed to save long-term memory.")
            raise

    # =========================================================
    # Retrieval
    # =========================================================

    async def get_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 100,
    ) -> list[Memory]:
        """
        Return conversation messages in chronological order.
        """

        result = await self.db.execute(
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.conversation_id == conversation_id,
                Memory.memory_type == MemoryType.CONVERSATION.value,
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
        """
        Return long-term memories ordered by importance.
        """

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

    # =========================================================
    # Qdrant Synchronization
    # =========================================================

    async def update_qdrant_point(
        self,
        *,
        memory: Memory,
        point_id: str,
    ) -> Memory:
        """
        Store Qdrant point ID after vector insertion.
        """

        memory.qdrant_point_id = point_id

        await self.db.flush()
        await self.db.refresh(memory)

        return memory

    # =========================================================
    # Delete
    # =========================================================

    async def delete_memory(
        self,
        memory_id: UUID,
    ) -> None:
        """
        Delete one memory.
        """

        await self.db.execute(
            delete(Memory).where(
                Memory.id == memory_id
            )
        )

        await self.db.flush()

    async def delete_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
    ) -> None:
        """
        Delete an entire conversation.
        """

        await self.db.execute(
            delete(Memory).where(
                Memory.user_id == user_id,
                Memory.conversation_id == conversation_id,
                Memory.memory_type == MemoryType.CONVERSATION.value,
            )
        )

        await self.db.flush()

    # =========================================================
    # Statistics
    # =========================================================

    async def memory_count(
        self,
        *,
        user_id: UUID,
    ) -> int:
        """
        Count long-term memories for a user.
        """

        result = await self.db.execute(
            select(func.count())
            .select_from(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.memory_type == MemoryType.LONG_TERM.value,
            )
        )

        return int(result.scalar() or 0)

    # =========================================================
    # Health
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify database connectivity.
        """

        try:
            await self.db.execute(select(1))
            return True

        except Exception:
            logger.exception(
                "PostgreSQL memory health check failed."
            )
            return False