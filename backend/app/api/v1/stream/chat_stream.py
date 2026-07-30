from __future__ import annotations

import json
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from app.ai.brain import AuraBrain
from app.api.dependencies import get_aura_brain
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.api.v1.chat import ChatRequest

router = APIRouter(
    prefix="/stream",
    tags=["Streaming"],
)


@router.post("/chat")
async def stream_chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    brain: AuraBrain = Depends(get_aura_brain),
):
    """
    Streams AI response token-by-token.
    """

    conversation_id = (
        request.conversation_id or uuid4()
    )

    async def event_generator():

        async for chunk in brain.stream_chat(
            user_id=user.id,
            conversation_id=conversation_id,
            message=request.message,
            metadata=request.metadata,
        ):

            yield (
                f"data: {json.dumps({'token': chunk})}\n\n"
            )

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )