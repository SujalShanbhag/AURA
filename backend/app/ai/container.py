from __future__ import annotations

from functools import lru_cache

from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis

from app.ai.brain import AuraBrain
from app.ai.orchestrator import Orchestrator
from app.ai.provider_registry import ProviderRegistry
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.ollama import OllamaProvider
from app.core.config import settings
from app.memory.manager import MemoryManager
from app.memory.qdrant_memory import QdrantMemory
from app.memory.redis_memory import RedisMemory
from app.memory.postgres_memory import PostgresMemory
from app.core.database import AsyncSessionLocal


class AIContainer:
    """
    Production AURA dependency container.

    Creates:

    - AI Providers
    - AI Orchestrator
    - Memory Systems
    - AURA Brain
    """


    def __init__(self):

        self.registry = (
            ProviderRegistry()
        )


        self._register_providers()


        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )


        self.redis_memory = RedisMemory(
            self.redis_client
        )


        self.qdrant_client = AsyncQdrantClient(
            url=settings.QDRANT_URL
        )


        self.qdrant_memory = QdrantMemory(
            client=self.qdrant_client,
            collection_name=(
                settings.QDRANT_COLLECTION
            ),
            vector_size=(
                settings.QDRANT_VECTOR_SIZE
            ),
        )


        self.postgres_memory = None


        self.memory_manager = None


        self.orchestrator = Orchestrator(
            registry=self.registry,

            primary_provider=(
                settings.AI_PRIMARY_PROVIDER
            ),

            fallback_providers=(
                settings.AI_FALLBACK_PROVIDERS
            ),

            max_retries=(
                settings.AI_MAX_RETRIES
            ),
        )


        self.brain = None



    def _register_providers(
        self,
    ):
        """
        Register AI providers.
        """

        self.registry.register(
            GeminiProvider()
        )


        self.registry.register(
            OpenAIProvider()
        )


        self.registry.register(
            OllamaProvider()
        )



    async def initialize_memory(
        self,
    ):
        """
        Initialize database-backed memory.

        Called during application startup.
        """

        db = AsyncSessionLocal()


        self.postgres_memory = (
            PostgresMemory(
                db
            )
        )


        self.memory_manager = MemoryManager(
            redis_memory=self.redis_memory,

            postgres_memory=(
                self.postgres_memory
            ),

            qdrant_memory=(
                self.qdrant_memory
            ),
        )


        self.brain = AuraBrain(
            orchestrator=self.orchestrator,

            memory=self.memory_manager,
        )



    def get_brain(
        self,
    ) -> AuraBrain:
        """
        Return initialized AURA Brain.
        """

        if self.brain is None:
            raise RuntimeError(
                "AI Container not initialized."
            )


        return self.brain



@lru_cache
def get_ai_container() -> AIContainer:
    """
    Singleton container.
    """

    return AIContainer()



async def initialize_ai():
    """
    Application startup hook.
    """

    container = (
        get_ai_container()
    )

    await container.initialize_memory()



def get_aura_brain() -> AuraBrain:
    """
    FastAPI dependency.
    """

    return (
        get_ai_container()
        .get_brain()
    )