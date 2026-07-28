from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean

from app.models.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    full_name = Column(String(255))

    hashed_password = Column(String(255), nullable=False)

    avatar = Column(String(500), nullable=True)

    language = Column(String(20), default="en")

    theme = Column(String(20), default="dark")

    is_active = Column(Boolean, default=True)