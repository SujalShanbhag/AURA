from __future__ import annotations


from uuid import UUID


from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer


from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db

from app.core.security import validate_token

from app.repositories.user_repository import UserRepository



# ============================================================
# OAuth2 Configuration
# ============================================================


oauth2_scheme = OAuth2PasswordBearer(

    tokenUrl="/api/v1/auth/login"

)



# ============================================================
# Current User Dependency
# ============================================================


async def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: AsyncSession = Depends(get_db),

):

    """
    Validate JWT access token
    and return authenticated user.
    """


    # --------------------------------------------------------
    # Validate JWT
    # --------------------------------------------------------

    try:

        payload = validate_token(

            token,

            expected_type="access",

        )


    except ValueError as exc:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=str(exc),

            headers={
                "WWW-Authenticate": "Bearer"
            },

        )



    # --------------------------------------------------------
    # Extract User ID
    # --------------------------------------------------------

    user_id = payload.get(
        "sub"
    )


    if not user_id:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid token subject.",

        )



    try:

        user_uuid = UUID(
            user_id
        )


    except ValueError:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid user identifier.",

        )



    # --------------------------------------------------------
    # Fetch User
    # --------------------------------------------------------

    user_repository = UserRepository(
        db
    )


    user = await user_repository.get_by_id(
        user_uuid
    )



    if user is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found.",

        )



    # --------------------------------------------------------
    # Account Status
    # --------------------------------------------------------

    if not user.is_active:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="User account is disabled.",

        )



    return user