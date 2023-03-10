from __future__ import annotations

import asyncio
from http import HTTPStatus
from typing import Any

import pytest
from fixtures.elastic import FixtureTypeElasticDataWriter
from fixtures.http import FixtureTypeGetRequestMaker
from redis.asyncio import Redis
from settings import settings
from testdata.data_movies import (
    expected_film_data,
    film_work_data,
    not_found_film_data,
)
from testdata.movies_params import film_list_params, film_search_params
from utils.logger import get_logger
from utils.test_utils import check_films_result, query_to_key_movies

logger = get_logger(__name__)


@pytest.mark.parametrize(
    'endpoint, query, expected_status', [*film_search_params, *film_list_params]
)
@pytest.mark.asyncio
async def test_get_list_films(
    es_write_data: FixtureTypeElasticDataWriter,
    make_get_request: FixtureTypeGetRequestMaker,
    endpoint: str,
    query: dict[str, Any],
    expected_status: int,
    redis_cache: Redis[Any],
) -> None:
    redis_key = query_to_key_movies(query)

    assert await redis_cache.get(redis_key) is None

    await es_write_data(film_work_data, settings.movies_index)
    await asyncio.sleep(1)

    response = await make_get_request(endpoint=f'{endpoint}', params=query)
    assert response.status == expected_status

    if query.get('query') == 'Star' and expected_status == HTTPStatus.OK:
        assert isinstance(response.body, list)
        check_films_result(
            status=response.status,
            expected_status=expected_status,
            body=response.body,
            expected_query=query.get('query'),
        )
    if not expected_status == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert await redis_cache.get(redis_key) is not None


@pytest.mark.asyncio
async def test_get_film(
    make_get_request: FixtureTypeGetRequestMaker, redis_cache: Redis[Any]
) -> None:
    response = await make_get_request(
        endpoint=f'films/{expected_film_data.get("id")}', params={}
    )
    await asyncio.sleep(1)

    assert HTTPStatus.OK == response.status
    assert isinstance(response.body, dict)

    assert expected_film_data.get('id') == response.body.get('id')

    assert expected_film_data.get('title') == response.body.get('title')

    assert expected_film_data.get('imdb_rating') == response.body.get('imdb_rating')

    assert expected_film_data.get('description') == response.body.get('description')

    assert expected_film_data.get('genres') == response.body.get('genres')

    assert expected_film_data.get('actors') == response.body.get('actors')

    assert expected_film_data.get('writers') == response.body.get('writers')

    assert expected_film_data.get('director') == response.body.get('director')

    redis_key = f'movies:{expected_film_data.get("id")}'
    assert await redis_cache.get(redis_key) is not None
    await redis_cache.flushall()

    assert await redis_cache.get(redis_key) is None

    response = await make_get_request(
        endpoint=f'films/{not_found_film_data.get("id")}', params={}
    )

    assert HTTPStatus.NOT_FOUND == response.status

    redis_key = f'movies:{not_found_film_data.get("id")}'

    assert await redis_cache.get(redis_key) is not None

    await redis_cache.flushall()

    assert await redis_cache.get(redis_key) is None
