from __future__ import annotations

from typing import Any, Optional

from redis.asyncio import Redis

redis: Optional[Redis[Any]] = None


async def get_redis() -> Redis[Any]:
    if not redis:
        raise Exception('Redis not initialized yet.')
    return redis
