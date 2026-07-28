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

    id: int

    username: str

    email: EmailStr

    full_name: str

    avatar: str | None = None

    class Config:
        from_attributes = True