from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator

from app.ai.brain import AuraBrain
from app.api.dependencies import get_aura_brain
from app.api.dependencies.auth import get_current_user
from app.models.user import User


logger = logging.getLogger("aura.api.chat")


router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"],
)


# ============================================================
# Request Schema
# ============================================================

class ChatRequest(BaseModel):
    """
    Request sent by the client.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    conversation_id: UUID | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        return value


# ============================================================
# Response Schema
# ============================================================

class ChatResponse(BaseModel):
    """
    Standard chat response.
    """

    conversation_id: UUID

    response: str

    provider: str

    model: str

    created_at: datetime


# ============================================================
# Chat Endpoint
# ============================================================

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    brain: AuraBrain = Depends(get_aura_brain),
):
    """
    Main AURA conversation endpoint.

    Flow:

    User
        ↓
    FastAPI
        ↓
    AuraBrain
        ↓
    Memory Retrieval
        ↓
    AI Orchestrator
        ↓
    AI Provider
        ↓
    Response
    """

    conversation_id = request.conversation_id or uuid4()

    try:

        result = await brain.chat(
            user_id=user.id,
            conversation_id=conversation_id,
            message=request.message,
            metadata=request.metadata,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            response=result.content,
            provider=result.provider.name,
            model=result.provider.model,
            created_at=result.created_at
            if result.created_at
            else datetime.now(timezone.utc),
        )

    except ValueError as exc:

        logger.warning(
            "Chat validation error: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except TimeoutError:

        logger.exception(
            "AI provider timeout.",
        )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI provider timed out. Please try again.",
        )

    except RuntimeError as exc:

        logger.exception(
            "AI processing failed.",
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected chat failure.",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        ) from exc