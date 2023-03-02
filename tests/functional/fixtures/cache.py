from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from redis import asyncio as aioredis
from settings import settings


@pytest_asyncio.fixture()
async def redis_cache() -> AsyncGenerator[aioredis.Redis[Any], None]:
    cache = aioredis.from_url(f'redis://{settings.redis_host}:{settings.redis_port}')
    await cache.flushall()
    yield cache
    await cache.close()
