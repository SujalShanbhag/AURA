from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any

from jose import JWTError
from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings


# --------------------------------------------------------------------
# Password Hashing (Argon2id)
# --------------------------------------------------------------------

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against an Argon2id hash.
    """
    return password_hasher.verify(password, password_hash)


# --------------------------------------------------------------------
# JWT Helpers
# --------------------------------------------------------------------

ALGORITHM = "HS256"


def _create_token(
    *,
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    extra: dict[str, Any] | None = None,
) -> str:

    now = datetime.now(timezone.utc)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }

    if extra:
        payload.update(extra)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_access_token(
    user_id: str,
) -> str:

    return _create_token(
        subject=user_id,
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
        token_type="access",
    )


def create_refresh_token(
    user_id: str,
    token_id: str,
) -> str:

    return _create_token(
        subject=user_id,
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        ),
        token_type="refresh",
        extra={
            "jti": token_id,
        },
    )


# --------------------------------------------------------------------
# JWT Decode
# --------------------------------------------------------------------


def decode_token(
    token: str,
) -> dict[str, Any]:

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[ALGORITHM],
    )


def validate_token(
    token: str,
    expected_type: str,
) -> dict[str, Any]:

    try:

        payload = decode_token(token)

        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type.")

        return payload

    except JWTError as exc:
        raise ValueError("Invalid or expired token.") from exc


# --------------------------------------------------------------------
# Refresh Token Hashing
# --------------------------------------------------------------------


def hash_refresh_token(
    refresh_token: str,
) -> str:

    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()


# --------------------------------------------------------------------
# Secure Random Tokens
# --------------------------------------------------------------------


def generate_secure_token(
    length: int = 64,
) -> str:
    """
    Generates a URL-safe cryptographically secure token.
    """

    return secrets.token_urlsafe(length)


def generate_token_id() -> str:
    """
    Generates a random JWT ID.
    """

    return secrets.token_hex(32)