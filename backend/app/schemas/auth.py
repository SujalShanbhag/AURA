from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


# ---------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------


class RegisterRequest(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    full_name: str = Field(
        min_length=2,
        max_length=120,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


# ---------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------


class LoginRequest(BaseModel):
    """
    Client login request.

    Network-related values such as IP address and
    User-Agent are obtained from the HTTP request,
    not from the request body.
    """

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    device_name: str = Field(
        max_length=120,
    )

    device_type: str = Field(
        max_length=50,
    )

    operating_system: str = Field(
        max_length=100,
    )

    browser: str | None = None


# ---------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------


class LogoutRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------------------
# Password Reset
# ---------------------------------------------------------------------


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


# ---------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------


class VerifyEmailRequest(BaseModel):
    token: str


# ---------------------------------------------------------------------
# User Response
# ---------------------------------------------------------------------


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    email: EmailStr

    username: str

    full_name: str

    avatar_url: str | None

    language: str

    timezone: str

    is_active: bool

    is_verified: bool

    is_superuser: bool

    created_at: datetime

    updated_at: datetime


# ---------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------


class TokenPair(BaseModel):
    access_token: str

    refresh_token: str

    token_type: str = "bearer"


# ---------------------------------------------------------------------
# Authentication Response
# ---------------------------------------------------------------------


class AuthResponse(BaseModel):
    user: UserResponse

    tokens: TokenPair


# ---------------------------------------------------------------------
# Session Response
# ---------------------------------------------------------------------


class SessionResponse(BaseModel):
    id: UUID

    device_name: str

    device_type: str

    operating_system: str

    browser: str | None

    ip_address: str

    country: str | None

    city: str | None

    is_current: bool

    created_at: datetime

    last_seen_at: datetime

    expires_at: datetime


# ---------------------------------------------------------------------
# Generic Message
# ---------------------------------------------------------------------


class MessageResponse(BaseModel):
    message: str