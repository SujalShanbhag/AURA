from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


def create_user(db: Session, user):

    db_user = User(

        username=user.username,

        email=user.email,

        full_name=user.full_name,

        hashed_password=hash_password(user.password)

    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user