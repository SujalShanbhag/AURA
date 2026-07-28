from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.user import UserCreate

from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(

    user: UserCreate,

    db: Session = Depends(get_db)

):

    new_user = create_user(db, user)

    return {

        "message": "User Created",

        "user": new_user.email

    }