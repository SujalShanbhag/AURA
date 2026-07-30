from uuid import UUID

from aura.backend.app.models import user
from pydantic import BaseModel
from pydantic import EmailStr


class UserCreate(BaseModel):

    username: str

    email: EmailStr

    full_name: str

    password: str


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class UserResponse(BaseModel):

    id: UUID

    username: str

    email: str

    full_name: str

    avatar: str | None = None

    model_config = {
        "from_attributes": True
    }
    "user": UserResponse.model_validate(user)