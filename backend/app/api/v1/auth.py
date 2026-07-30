from __future__ import annotations


import logging

from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status


from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db

from app.core.auth import get_current_user


from app.models.user import User


from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
)


from app.services.auth_service import AuthService



logger = logging.getLogger(
    "aura.api.auth"
)



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)





# ============================================================
# Dependency
# ============================================================


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:

    return AuthService(db)





# ============================================================
# Register
# ============================================================


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

    try:

        user = await service.register(
            request
        )


        return {

            "message":
                "User registered successfully.",


            "user": {

                "id":
                    str(user.id),

                "email":
                    user.email,

                "username":
                    user.username,

                "full_name":
                    user.full_name,

            },

        }



    except ValueError as exc:


        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=str(exc),

        )





# ============================================================
# Login
# ============================================================


@router.post(
    "/login"
)
async def login(

    body: LoginRequest,

    request: Request,

    service: AuthService = Depends(
        get_auth_service
    ),

):


    ip_address = (

        request.client.host

        if request.client

        else "unknown"

    )


    user_agent = request.headers.get(
        "User-Agent",
        "",
    )


    # attach request metadata

    body.ip_address = ip_address

    body.user_agent = user_agent



    try:

        result = await service.login(
            body
        )


        return {

            "message":
                "Login successful.",


            "user": {

                "id":
                    str(
                        result["user"].id
                    ),

                "email":
                    result["user"].email,

                "username":
                    result["user"].username,

            },


            "tokens":
                result["tokens"],

        }



    except ValueError as exc:


        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=str(exc),

        )





# ============================================================
# Refresh Token
# ============================================================


@router.post(
    "/refresh"
)
async def refresh(

    request: RefreshRequest,

    service: AuthService = Depends(
        get_auth_service
    ),

):

    try:

        return await service.refresh(

            request.refresh_token

        )


    except ValueError as exc:


        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=str(exc),

        )





# ============================================================
# Logout Current Session
# ============================================================


@router.post(
    "/logout/{session_id}"
)
async def logout(

    session_id: UUID,

    service: AuthService = Depends(
        get_auth_service
    ),

):

    await service.logout(
        session_id
    )


    return {

        "message":
            "Logged out successfully."

    }





# ============================================================
# Logout All Devices
# ============================================================


@router.post(
    "/logout-all"
)
async def logout_all(

    current_user: User = Depends(
        get_current_user
    ),

    service: AuthService = Depends(
        get_auth_service
    ),

):


    await service.logout_all(

        current_user.id

    )


    return {

        "message":
            "All sessions logged out successfully."

    }