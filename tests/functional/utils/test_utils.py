from typing import Any, Type

from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)


def refactor(string: str) -> str:
    logger.info(f'YYYYYYYYYY {string}')
    return string.replace('/', '.').replace('\\', '.').replace('.py', '')


class BaseQuery(BaseModel):
    sort: str | None = None
    size: int | None = Field(None, alias='page[size]')
    page_num: int | None = Field(None, alias='page[number]')
    query: str | None = None


class MovieQuery(BaseQuery):
    genre: str | None = Field(None, alias='filter[genre]')
    writers: str | None = Field(None, alias='filter[writers]')
    actors: str | None = Field(None, alias='filter[actor]')
    directors: str | None = Field(None, alias='filter[director]')


class PersonQuery(BaseQuery):
    film_ids: str | None = Field(None, alias='filter[film_ids]')


def query_to_key(query: dict[str, Any], model: Type[BaseModel]) -> str:
    result = model(**query)
    return str(dict(sorted(result.dict().items(), key=lambda x: x[0])))


def query_to_key_movies(query: dict[str, Any]) -> str:
    return query_to_key(query, MovieQuery)


def query_to_key_genres(query: dict[str, Any]) -> str:
    return query_to_key(query, BaseQuery)


def query_to_key_persons(query: dict[str, Any]) -> str:
    return query_to_key(query, PersonQuery)


def check_films_result(
    status: int,
    expected_status: int,
    body: list[dict[str, Any]],
    expected_query: str | None,
) -> None:
    """
    Compare expected values with the results of the queries.
    """
    result_response: list[str] = [res['title'] for res in body if 'title' in res]
    for row in result_response:
        if expected_query:
            assert expected_query in row
