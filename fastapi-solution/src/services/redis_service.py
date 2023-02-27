from __future__ import annotations

from collections.abc import Sequence as Sq
from typing import Any, Sequence, Type

import orjson
from core.backoff import backoff_function
from core.config import settings
from core.logger import get_logger
from pydantic import BaseModel
from redis.asyncio import Redis, RedisError
from redis.exceptions import ConnectionError
from services.ancestors import AsyncCacheStorage

logger = get_logger(__name__)


class RedisService(AsyncCacheStorage):
    def __init__(self, redis: Redis[Any]) -> None:
        self.redis = redis

    @backoff_function(RedisError, ConnectionError)
    async def _list_all_keys(self) -> list[str]:
        return await self.redis.keys('*')

    @backoff_function(RedisError, ConnectionError)
    async def get(
        self, key: str, model: Type[BaseModel]
    ) -> BaseModel | Sequence[BaseModel] | None:
        if data := await self.redis.get(key):
            data = orjson.loads(data)
            if isinstance(data, Sq):
                return self.parse_several_objects(data, model)
            return self.parse_single_object(data, model)
        return data

    @backoff_function(RedisError, ConnectionError)
    async def put(self, key: str, data: None | BaseModel | Sequence[BaseModel]) -> None:
        if isinstance(data, Sq):
            data_str: str | bytes = orjson.dumps([obj.json() for obj in data])
        elif data:
            data_str = data.json()
        else:
            data_str = ''
        await self.redis.set(key, data_str, ex=settings.cache_expired)

    def parse_single_object(
        self, data: dict[str, Any], model: Type[BaseModel]
    ) -> BaseModel | None:
        try:
            return model(**data)
        except Exception as e:
            logger.error(f'Error while parsing single object from cache: {e}')
        return None

    def parse_several_objects(
        self, data: Sequence[Any], model: Type[BaseModel]
    ) -> Sequence[BaseModel] | None:
        try:
            return [model(**orjson.loads(obj)) for obj in data]
        except Exception as e:
            logger.error(f'Error while parsing several objects from cache: {e}')
        return None
