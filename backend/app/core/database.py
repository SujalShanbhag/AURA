from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger("aura.database")

# ============================================================
# Database Engine
# ============================================================

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_reset_on_return="rollback",
)

# ============================================================
# Session Factory
# ============================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Backward compatibility
async_session_factory = AsyncSessionLocal

# ============================================================
# Base Model
# ============================================================

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """

    pass

# ============================================================
# FastAPI Dependency
# ============================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async SQLAlchemy session.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# ============================================================
# Database Health Check
# ============================================================

async def database_health_check() -> bool:
    """
    Verify database connectivity.
    """

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True

    except Exception:
        logger.exception("Database health check failed.")
        return False

# ============================================================
# Shutdown
# ============================================================

async def close_database() -> None:
    """
    Dispose the SQLAlchemy engine.
    """

    await engine.dispose()

    logger.info("Database engine disposed.")