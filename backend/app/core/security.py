from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import settings

logger = logging.getLogger("aura.security")

# ============================================================
# Password Hashing
# ============================================================

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.
    """

    password = password.strip()

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a password against its stored hash.
    """

    try:
        return password_hasher.verify(
            password,
            password_hash,
        )

    except Exception:
        logger.exception("Password verification failed.")
        return False


def verify_and_update_password(
    password: str,
    password_hash: str,
) -> tuple[bool, str | None]:
    """
    Verify password and return an updated hash if the
    hashing parameters have changed.
    """

    try:
        valid, new_hash = password_hasher.verify_and_update(
            password,
            password_hash,
        )

        return valid, new_hash

    except Exception:
        logger.exception("Password verification/update failed.")
        return False, None


# ============================================================
# JWT Creation
# ============================================================

def _create_token(
    *,
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    extra: dict[str, Any] | None = None,
) -> str:
    """
    Internal JWT generator.
    """

    now = datetime.now(timezone.utc)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }

    if extra:
        payload.update(extra)

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(
    user_id: str,
) -> str:
    """
    Create JWT access token.
    """

    return _create_token(
        subject=user_id,
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        token_type="access",
    )


def create_refresh_token(
    user_id: str,
    token_id: str,
) -> str:
    """
    Create JWT refresh token.
    """

    return _create_token(
        subject=user_id,
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        token_type="refresh",
        extra={
            "jti": token_id,
        },
    )


# ============================================================
# JWT Validation
# ============================================================

def decode_token(
    token: str,
) -> dict[str, Any]:
    """
    Decode and validate JWT.
    """

    if not token:
        raise ValueError("Token cannot be empty.")

    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )

    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token."
        ) from exc


def validate_token(
    token: str,
    expected_type: str,
) -> dict[str, Any]:
    """
    Validate token type and required claims.
    """

    payload = decode_token(token)

    if payload.get("type") != expected_type:
        raise ValueError(
            "Invalid token type."
        )

    if not payload.get("sub"):
        raise ValueError(
            "Missing token subject."
        )

    if expected_type == "refresh":
        if not payload.get("jti"):
            raise ValueError(
                "Missing refresh token id."
            )

    return payload


# ============================================================
# Refresh Token Security
# ============================================================

def hash_refresh_token(
    refresh_token: str,
) -> str:
    """
    SHA-256 hash for refresh tokens.
    """

    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()


# ============================================================
# Secure Token Generation
# ============================================================

def generate_secure_token(
    length: int = 64,
) -> str:
    """
    Generate a cryptographically secure random token.
    """

    return secrets.token_urlsafe(length)


def generate_token_id() -> str:
    """
    Generate a unique token identifier (JTI).
    """

    return secrets.token_hex(32)