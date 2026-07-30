from __future__ import annotations

import logging
import time
from datetime import datetime
from datetime import timezone
from typing import AsyncIterator

from google import genai

from app.ai.models import (
    AIContext,
    AIProviderInfo,
    AIResponse,
    AIStreamChunk,
    TokenUsage,
)
from app.ai.provider import AIProvider
from app.core.config import settings


logger = logging.getLogger(
    "aura.ai.providers.gemini"
)


class GeminiProvider(AIProvider):
    """
    Google Gemini AI Provider.

    Supports:

    - Text generation
    - Streaming
    - Token usage tracking
    - Health monitoring
    """


    def __init__(
        self,
        model: str | None = None,
    ):

        self._model = (
            model
            or settings.GEMINI_MODEL
        )


        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )


    # =========================================================
    # Provider Metadata
    # =========================================================


    @property
    def name(
        self,
    ) -> str:

        return "gemini"


    @property
    def model(
        self,
    ) -> str:

        return self._model


    @property
    def supports_streaming(
        self,
    ) -> bool:

        return True


    @property
    def supports_tools(
        self,
    ) -> bool:

        return False



    # =========================================================
    # Prompt Builder
    # =========================================================


    def _build_prompt(
        self,
        context: AIContext,
    ) -> str:

        parts: list[str] = []


        if context.system_prompt:

            parts.append(
                context.system_prompt
            )


        semantic_memory = (
            context.metadata.get(
                "semantic_memory"
            )
        )


        if semantic_memory:

            parts.append(
                "\nRelevant memories:"
            )

            for memory in semantic_memory:

                parts.append(
                    f"- {memory}"
                )


        history = (
            context.metadata.get(
                "recent_history"
            )
        )


        if history:

            parts.append(
                "\nConversation history:"
            )

            for message in history:

                parts.append(
                    str(message)
                )


        parts.append(
            f"\nUser: {context.message}"
        )


        return "\n".join(parts)



    # =========================================================
    # Generate Response
    # =========================================================


    async def generate(
        self,
        context: AIContext,
    ) -> AIResponse:


        start = time.perf_counter()


        prompt = self._build_prompt(
            context
        )


        try:

            response = await (
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
            )


            latency = (
                time.perf_counter()
                -
                start
            ) * 1000


            usage = TokenUsage()


            usage_data = getattr(
                response,
                "usage_metadata",
                None,
            )


            if usage_data:

                usage = TokenUsage(
                    prompt_tokens=getattr(
                        usage_data,
                        "prompt_token_count",
                        0,
                    ),

                    completion_tokens=getattr(
                        usage_data,
                        "candidates_token_count",
                        0,
                    ),

                    total_tokens=getattr(
                        usage_data,
                        "total_token_count",
                        0,
                    ),
                )


            content = (
                getattr(
                    response,
                    "text",
                    None,
                )
                or ""
            )


            return AIResponse(

                content=content,


                provider=AIProviderInfo(
                    name=self.name,
                    model=self.model,
                    latency_ms=latency,
                    supports_streaming=True,
                    supports_tools=False,
                ),


                usage=usage,


                metadata={
                    "request_id": str(
                        context.request_id
                    )
                },


                created_at=datetime.now(
                    timezone.utc
                ),
            )


        except Exception as exc:


            logger.exception(
                "Gemini generation failed."
            )


            raise RuntimeError(
                "Gemini provider failed."
            ) from exc



    # =========================================================
    # Streaming
    # =========================================================


    async def stream(
        self,
        context: AIContext,
    ) -> AsyncIterator[str]:


        prompt = self._build_prompt(
            context
        )


        try:


            stream = (
                self.client.aio.models.generate_content_stream(
                    model=self.model,
                    contents=prompt,
                )
            )


            async for chunk in stream:


                text = getattr(
                    chunk,
                    "text",
                    None,
                )


                if text:

                    yield text



        except Exception as exc:


            logger.exception(
                "Gemini streaming failed."
            )


            raise RuntimeError(
                "Gemini streaming failed."
            ) from exc



    # =========================================================
    # Health Check
    # =========================================================


    async def health_check(
        self,
    ) -> bool:


        try:


            await (
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents="ping",
                )
            )


            return True



        except Exception:


            logger.exception(
                "Gemini health check failed."
            )


            return False



    # =========================================================
    # Cleanup
    # =========================================================


    async def close(
        self,
    ) -> None:

        return None