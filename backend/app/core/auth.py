from __future__ import annotations


from uuid import UUID


from fastapi import Depends, HTTPException, status


from fastapi.security import OAuth2PasswordBearer


from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db


from app.core.security import validate_token


from app.repositories.user_repository import UserRepository





oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)





async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    try:

        payload = validate_token(
            token,
            "access",
        )


        user_id = UUID(
            payload["sub"]
        )


    except Exception:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid authentication token.",

            headers={
                "WWW-Authenticate": "Bearer"
            },

        )



    users = UserRepository(
        db
    )


    user = await users.get_by_id(
        user_id
    )


    if user is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found.",

        )



    if not user.is_active:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="User account disabled.",

        )



    return user