from __future__ import annotations

import asyncio
from http import HTTPStatus
from typing import Any

import pytest
from fixtures.elastic import FixtureTypeElasticDataWriter
from fixtures.http import FixtureTypeGetRequestMaker
from redis.asyncio import Redis
from schemas.genre_schema import FilmGenreValidation
from settings import settings
from testdata.data_genres import data_genres
from utils.logger import get_logger
from utils.test_utils import query_to_key_genres

logger = get_logger(__name__)


@pytest.mark.asyncio
async def test_list_genre(
    es_write_data: FixtureTypeElasticDataWriter,
    make_get_request: FixtureTypeGetRequestMaker,
    redis_cache: Redis[Any],
) -> None:

    await es_write_data(data_genres, settings.genre_index)
    redis_key = query_to_key_genres({})

    assert await redis_cache.get(redis_key) is None

    await asyncio.sleep(3)
    response = await make_get_request(endpoint='genres/', params={})
    response_body = response.body
    assert response.status == HTTPStatus.OK
    assert isinstance(response_body, list)

    assert len(response_body) == len(data_genres)

    for genre in data_genres:
        for response_genre in response_body:
            if genre.get('id') == response_genre.get('id'):

                assert genre.get('id') == response_genre.get('id')

                assert genre.get('name') == response_genre.get('name')


@pytest.mark.asyncio
async def test_genre_by_id(
    make_get_request: FixtureTypeGetRequestMaker, redis_cache: Redis[Any]
) -> None:
    for test_genre in data_genres:
        genre_id = test_genre.get('id')
        response = await make_get_request(endpoint=f'genres/{genre_id}', params={})
        response_body = response.body

        assert response.status == HTTPStatus.OK
        assert isinstance(response_body, dict)

        assert FilmGenreValidation(**response_body)

        assert test_genre.get('id') == response_body.get('id')

        assert test_genre.get('name') == response_body.get('name')

        assert await redis_cache.get(f'genres:{genre_id}') is not None

        await redis_cache.flushall()

        assert await redis_cache.get(f'genres:{genre_id}') is None
