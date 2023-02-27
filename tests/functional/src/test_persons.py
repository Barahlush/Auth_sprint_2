from __future__ import annotations

import asyncio
from http import HTTPStatus
from typing import Any

import pytest
from fixtures.elastic import FixtureTypeElasticDataWriter
from fixtures.http import FixtureTypeGetRequestMaker, HTTPResponse
from redis.asyncio import Redis
from schemas.person_schema import DetailPersonValidation
from settings import settings
from testdata.data_persons import person_data
from utils.logger import get_logger
from utils.test_utils import query_to_key_persons

logger = get_logger(__name__)


@pytest.mark.asyncio
async def test_person_by_id(
    es_write_data: FixtureTypeElasticDataWriter,
    make_get_request: FixtureTypeGetRequestMaker,
    redis_cache: Redis[Any],
) -> None:
    await es_write_data(person_data, settings.person_index)
    await asyncio.sleep(1)

    for person in person_data:
        person_id = person.get('id')
        response: HTTPResponse = await make_get_request(
            endpoint=f'persons/{person_id}', params={}
        )

        response_body = response.body

        assert response.status == HTTPStatus.OK
        assert isinstance(response_body, dict)

        assert DetailPersonValidation(**response_body)

        assert response_body.get('id') == person_id

        assert response_body.get('name') == person.get('name')

        assert response_body.get('film_ids') == person.get('film_ids')

        assert await redis_cache.get(f'persons:{person_id}') is not None

        await redis_cache.flushall()
        assert await redis_cache.get(f'persons:{person_id}') is None


@pytest.mark.asyncio
async def test_search_person(
    make_get_request: FixtureTypeGetRequestMaker, redis_cache: Redis[Any]
) -> None:
    test_person: dict[str, str] = person_data[1]
    query: dict[str, Any] = {'query': 'Jake'}
    await asyncio.sleep(1)

    redis_key = query_to_key_persons(query)

    assert await redis_cache.get(redis_key) is None

    response = await make_get_request(endpoint='persons/', params=query)
    response_body = response.body
    assert isinstance(response_body, list)

    response_person: dict[str, str] = response_body[0]

    assert await redis_cache.get(redis_key) is not None

    assert response.status == HTTPStatus.OK

    assert response_person.get('id') == test_person.get('id')

    assert response_person.get('name') == test_person.get('name')

    assert query.get('query', '') in test_person.get('name', '')

    assert response_person.get('film_ids') == test_person.get('film_ids')


@pytest.mark.asyncio
async def test_list_person(
    make_get_request: FixtureTypeGetRequestMaker, redis_cache: Redis[Any]
) -> None:
    redis_key = query_to_key_persons({})

    assert await redis_cache.get(redis_key) is None

    response = await make_get_request(endpoint='persons/', params={})
    await asyncio.sleep(1)
    response_body = response.body

    assert await redis_cache.get(redis_key) is not None

    assert response.status == HTTPStatus.OK
    assert isinstance(response_body, list)

    assert len(response_body) == len(person_data)

    for person in person_data:
        for response_person in response_body:
            if person.get('id') == response_person.get('id'):

                assert person.get('id') == response_person.get('id')

                assert person.get('name') == response_person.get('name')

                assert person.get('film_ids') == response_person.get('film_ids')
