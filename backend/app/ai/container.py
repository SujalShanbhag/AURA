from __future__ import annotations

import logging
from functools import lru_cache

from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis

from app.ai.brain import AuraBrain
from app.ai.orchestrator import Orchestrator
from app.ai.provider_registry import ProviderRegistry
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.ollama import OllamaProvider
from app.ai.providers.openai import OpenAIProvider

from app.core.config import settings
from app.core.database import AsyncSessionLocal

from app.memory.embedding_service import EmbeddingService
from app.memory.memory_service import MemoryService
from app.memory.qdrant_memory import QdrantMemory
from app.memory.redis_memory import RedisMemory

logger = logging.getLogger("aura.ai.container")


class AIContainer:
    """
    Global dependency container.
    """

    def __init__(self) -> None:

        self.registry = ProviderRegistry()
        self._register_providers()

        if self.registry.count() == 0:
            raise RuntimeError("No AI providers are configured.")

        self.orchestrator = Orchestrator(
            registry=self.registry,
            primary_provider=settings.AI_PRIMARY_PROVIDER,
            fallback_providers=settings.AI_FALLBACK_PROVIDERS,
            max_retries=settings.AI_MAX_RETRIES,
        )

        # -----------------------------
        # Redis
        # -----------------------------

        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

        self.redis_memory = RedisMemory(self.redis_client)

        # -----------------------------
        # Qdrant
        # -----------------------------

        self.qdrant_client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=getattr(settings, "QDRANT_API_KEY", None),
        )

        self.qdrant_memory = QdrantMemory(
            client=self.qdrant_client,
            collection_name=settings.QDRANT_COLLECTION,
            vector_size=settings.QDRANT_VECTOR_SIZE,
        )

        # -----------------------------
        # Embeddings
        # -----------------------------

        self.embedding_service = EmbeddingService()

        # Created during startup
        self.db = None
        self.memory: MemoryService | None = None
        self.brain: AuraBrain | None = None

        self._initialized = False

    # =====================================================
    # Register AI Providers
    # =====================================================

    def _register_providers(self) -> None:

        if settings.GEMINI_API_KEY:
            self.registry.register(GeminiProvider())

        if settings.OPENAI_API_KEY:
            self.registry.register(OpenAIProvider())

        if getattr(settings, "OLLAMA_ENABLED", False):
            self.registry.register(OllamaProvider())

        logger.info(
            "Registered providers: %s",
            self.registry.list_providers(),
        )

    # =====================================================
    # Startup
    # =====================================================

    async def initialize(self) -> None:

        if self._initialized:
            return

        logger.info("Initializing AURA...")

        await self.qdrant_memory.initialize()

        # Database session
        self.db = AsyncSessionLocal()

        # Memory service
        self.memory = MemoryService(
            db=self.db,
            embedding_service=self.embedding_service,
            qdrant_memory=self.qdrant_memory,
        )

        # Brain
        self.brain = AuraBrain(
            orchestrator=self.orchestrator,
            memory=self.memory,
        )

        self._initialized = True

        logger.info("AURA initialized successfully.")

    # =====================================================
    # Shutdown
    # =====================================================

    async def shutdown(self) -> None:

        logger.info("Shutting down AURA...")

        try:
            await self.registry.shutdown()
        except Exception:
            logger.exception("Provider shutdown failed.")

        try:
            if self.memory:
                await self.memory.close()
        except Exception:
            logger.exception("Memory shutdown failed.")

        try:
            await self.embedding_service.close()
        except Exception:
            logger.exception("Embedding shutdown failed.")

        try:
            await self.redis_client.aclose()
        except Exception:
            logger.exception("Redis shutdown failed.")

        try:
            await self.qdrant_memory.close()
        except Exception:
            logger.exception("Qdrant shutdown failed.")

        try:
            if self.db:
                await self.db.close()
        except Exception:
            logger.exception("Database shutdown failed.")

        self._initialized = False

        logger.info("AURA shutdown complete.")


# =====================================================
# Singleton
# =====================================================

@lru_cache(maxsize=1)
def get_ai_container() -> AIContainer:
    return AIContainer()


# =====================================================
# FastAPI Lifecycle
# =====================================================

async def initialize_ai() -> None:
    await get_ai_container().initialize()


async def shutdown_ai() -> None:
    await get_ai_container().shutdown()