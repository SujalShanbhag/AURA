from __future__ import annotations

from datetime import datetime
from datetime import timezone
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory
from app.memory.models import ConversationMemory


class PostgresMemory:
    """
    Long-term memory storage.

    Uses PostgreSQL for:

    - Permanent conversation history
    - User memories
    - Important information
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
        """
        Save conversation permanently.
        """

        record = Memory(
            user_id=memory.user_id,
            conversation_id=(
                memory.conversation_id
            ),
            memory_type="conversation",
            role=memory.role,
            content=memory.message,
            metadata_json=(
                memory.metadata
            ),
            created_at=datetime.now(
                timezone.utc
            ),
        )


        self.db.add(
            record
        )

        await self.db.commit()

        await self.db.refresh(
            record
        )

        return record



    async def get_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 50,
    ) -> list[Memory]:
        """
        Retrieve conversation history.
        """

        query = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.conversation_id
                == conversation_id,
            )
            .order_by(
                Memory.created_at.asc()
            )
            .limit(limit)
        )


        result = await self.db.execute(
            query
        )


        return list(
            result.scalars().all()
        )



    async def save_user_memory(
        self,
        *,
        user_id: UUID,
        content: str,
        importance: float = 0.5,
        metadata: dict | None = None,
    ) -> Memory:
        """
        Save important user information.
        """

        record = Memory(
            user_id=user_id,
            memory_type="long_term",
            content=content,
            importance=importance,
            metadata_json=(
                metadata or {}
            ),
            created_at=datetime.now(
                timezone.utc
            ),
        )


        self.db.add(
            record
        )

        await self.db.commit()

        await self.db.refresh(
            record
        )

        return record



    async def get_user_memories(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
    ) -> list[Memory]:
        """
        Retrieve saved user memories.
        """

        query = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.memory_type
                == "long_term",
            )
            .order_by(
                Memory.importance.desc()
            )
            .limit(limit)
        )


        result = await self.db.execute(
            query
        )


        return list(
            result.scalars().all()
        )



    async def delete_memory(
        self,
        memory_id: UUID,
    ) -> None:
        """
        Remove stored memory.
        """

        await self.db.execute(
            delete(Memory)
            .where(
                Memory.id == memory_id
            )
        )


        await self.db.commit()