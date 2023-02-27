from __future__ import annotations

from functools import lru_cache
from typing import Any, Sequence, Type, cast

from core.logger import get_logger
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.films import Film, FilmFull
from models.genres import Genre, GenreFull
from models.persons import PersonFull
from services.ancestors import AsyncCacheStorage, SearchService
from services.elastic_service import ElasticService
from services.redis_service import RedisService
from services.utils import BulkModelType, ModelType

logger = get_logger(__name__)


class BaseService:
    def __init__(
        self,
        index: str,
        model_type: Type[ModelType],
        bulk_model_type: Type[BulkModelType],
        cache_service: AsyncCacheStorage,
        search_service: SearchService,
    ):
        self.index = index
        self.model_type = model_type
        self.bulk_model_type = bulk_model_type
        self.cache_service = cache_service
        self.search_service = search_service

    async def get_by_id(self, item_id: str) -> ModelType | None:
        """Getting item by id. Main Function."""
        redis_key = f'{self.index}:{item_id}'
        if item := await self.cache_service.get(redis_key, self.model_type):
            if isinstance(item, self.model_type):
                return item

        item = await self.search_service.get_one(item_id, self.index, self.model_type)
        await self.cache_service.put(redis_key, item)
        return cast(ModelType, item)

    async def get_items(self, **kwargs: Any) -> Sequence[BulkModelType]:
        """Getting items by params. Main Function."""

        redis_key = str(dict(sorted(kwargs.items(), key=lambda x: x[0])))
        items = await self.cache_service.get(redis_key, self.bulk_model_type)
        if isinstance(items, list):
            return items

        items = await self.search_service.get_several(
            self.index, self.bulk_model_type, None, False, **kwargs
        )
        items = items or []
        await self.cache_service.put(redis_key, items)

        return cast(Sequence[BulkModelType], items)


@lru_cache()
def get_genre_service(  # type: ignore
    cache=Depends(get_redis),
    search=Depends(get_elastic),
) -> BaseService:
    """GenreService provider."""
    cache_service = RedisService(cache)
    search_service = ElasticService(search)
    return BaseService('genres', GenreFull, Genre, cache_service, search_service)


@lru_cache()
def get_film_service(  # type: ignore
    cache=Depends(get_redis),
    search=Depends(get_elastic),
) -> BaseService:
    """FilmService provider."""
    cache_service = RedisService(cache)
    search_service = ElasticService(search)
    return BaseService('movies', FilmFull, Film, cache_service, search_service)


@lru_cache()
def get_person_service(  # type: ignore
    cache=Depends(get_redis),
    search=Depends(get_elastic),
) -> BaseService:
    """PersonService provider."""
    cache_service = RedisService(cache)
    search_service = ElasticService(search)
    return BaseService('persons', PersonFull, PersonFull, cache_service, search_service)
