from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    """
    Authentication service dependency.
    """

    return AuthService(db)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Create a new user account.
    """

    try:
        user = await service.register(
            request
        )

        return {
            "message": "User registered successfully.",
            "user": user,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/login",
)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Authenticate user.
    """

    try:

        return await service.login(
            request
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/refresh",
)
async def refresh(
    refresh_token: str,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Rotate refresh token.
    """

    try:

        return await service.refresh(
            refresh_token
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/logout/{session_id}",
)
async def logout(
    session_id: UUID,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Logout current device.
    """

    try:

        result = await service.logout(
            session_id
        )

        return {
            "message": "Logged out successfully.",
            "result": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/logout-all/{user_id}",
)
async def logout_all(
    user_id: UUID,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Logout all devices.
    """

    try:

        return await service.logout_all(
            user_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )