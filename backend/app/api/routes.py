from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.stream.chat_stream import router as stream_router

router = APIRouter()


# ---------------------------------------------------------
# System Endpoints
# ---------------------------------------------------------

@router.get(
    "/health",
    tags=["System"],
    summary="Health Check",
)
async def health():
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
        "service": "AURA API",
    }


# ---------------------------------------------------------
# API v1
# ---------------------------------------------------------

v1_router = APIRouter(
    prefix="/api/v1",
)


# Authentication
v1_router.include_router(
    auth_router,
    tags=["Authentication"],
)


# Standard Chat
v1_router.include_router(
    chat_router,
    tags=["Chat"],
)


# Streaming Chat
v1_router.include_router(
    stream_router,
    tags=["Streaming"],
)


router.include_router(v1_router)