from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

redis: Redis[Any] | None = None


async def get_redis() -> Redis[Any]:
    if not redis:
        raise Exception('Redis not initialized yet.')
    return redis
