from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import Field

from app.ai.brain import AuraBrain
from app.api.dependencies.auth import get_current_user
from app.ai.container import get_aura_brain


router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"],
)


class ChatRequest(BaseModel):
    """
    User chat request payload.
    """

    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    conversation_id: UUID | None = None

    metadata: dict = {}


class ChatResponse(BaseModel):
    """
    Chat response payload.
    """

    response: str

    provider: str

    model: str


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    user=Depends(get_current_user),
    brain: AuraBrain = Depends(
        get_aura_brain
    ),
):
    """
    Send message to AURA.
    """

    try:

        result = await brain.chat(
            user_id=user.id,
            message=request.message,
            conversation_id=(
                request.conversation_id
            ),
            metadata=request.metadata,
        )

        return ChatResponse(
            response=result.content,
            provider=result.provider.name,
            model=result.provider.model,
        )


    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )