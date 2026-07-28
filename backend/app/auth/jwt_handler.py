from datetime import datetime
from datetime import timedelta

from jose import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(days=7)

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=ALGORITHM,
    )