from __future__ import annotations

import time

from fastapi import HTTPException
from fastapi import Request
from redis.asyncio import Redis


class RateLimiter:
    """
    Redis-backed async rate limiter.

    Uses fixed window counters.

    Example:
        5 login attempts per minute per IP.
    """

    def __init__(
        self,
        redis: Redis,
        limit: int,
        window_seconds: int,
    ):
        self.redis = redis
        self.limit = limit
        self.window_seconds = window_seconds


    async def check(
        self,
        key: str,
    ) -> None:
        """
        Check whether request is allowed.
        """

        current_window = int(
            time.time()
            //
            self.window_seconds
        )

        redis_key = (
            f"rate_limit:"
            f"{key}:"
            f"{current_window}"
        )

        count = await self.redis.incr(
            redis_key
        )

        if count == 1:

            await self.redis.expire(
                redis_key,
                self.window_seconds,
            )


        if count > self.limit:

            raise HTTPException(
                status_code=429,
                detail=(
                    "Too many requests. "
                    "Please try again later."
                ),
            )


def get_client_ip(
    request: Request,
) -> str:
    """
    Extract client IP address.
    """

    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:

        return forwarded.split(
            ","
        )[0].strip()


    if request.client:

        return request.client.host


    return "unknown"


async def rate_limit(
    request: Request,
    limiter: RateLimiter,
):
    """
    FastAPI dependency wrapper.
    """

    ip = get_client_ip(
        request
    )

    await limiter.check(
        ip
    )