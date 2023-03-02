from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(
        self, key: str, model: type[BaseModel]
    ) -> BaseModel | Sequence[BaseModel] | None:
        pass

    @abstractmethod
    async def put(
        self, key: str, data: None | BaseModel | Sequence[BaseModel]
    ) -> None:
        pass

    @abstractmethod
    def parse_single_object(
        self, data: dict[str, Any], model: type[BaseModel]
    ) -> BaseModel | None:
        pass

    @abstractmethod
    def parse_several_objects(
        self, data: Sequence[Any], model: type[BaseModel]
    ) -> Sequence[BaseModel] | None:
        pass


class SearchService(ABC):
    @abstractmethod
    async def get_one(
        self, id: str, index: str, model: type[BaseModel]
    ) -> BaseModel | None:
        pass

    @abstractmethod
    async def get_several(
        self,
        index: str,
        model: type[BaseModel],
        query_params: list[str] | None,
        is_nested: bool = False,
        **kwargs: Any
    ) -> Sequence[BaseModel] | None:
        pass
