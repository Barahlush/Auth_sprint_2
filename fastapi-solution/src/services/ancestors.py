from abc import ABC, abstractmethod
from typing import Any, Sequence, Type

from pydantic import BaseModel


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(
        self, key: str, model: Type[BaseModel]
    ) -> BaseModel | Sequence[BaseModel] | None:
        pass

    @abstractmethod
    async def put(self, key: str, data: None | BaseModel | Sequence[BaseModel]) -> None:
        pass

    @abstractmethod
    def parse_single_object(
        self, data: dict[str, Any], model: Type[BaseModel]
    ) -> BaseModel | None:
        pass

    @abstractmethod
    def parse_several_objects(
        self, data: Sequence[Any], model: Type[BaseModel]
    ) -> Sequence[BaseModel] | None:
        pass


class SearchService(ABC):
    @abstractmethod
    async def get_one(
        self, id: str, index: str, model: Type[BaseModel]
    ) -> BaseModel | None:
        pass

    @abstractmethod
    async def get_several(
        self,
        index: str,
        model: Type[BaseModel],
        query_params: list[str] | None,
        is_nested: bool = False,
        **kwargs: Any
    ) -> Sequence[BaseModel] | None:
        pass
