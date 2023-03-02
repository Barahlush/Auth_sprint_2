from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any, Protocol

import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import BulkIndexError, async_bulk
from settings import settings
from utils.es_utils import build_indexes, get_es_bulk_query, remove_indexes
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest_asyncio.fixture(scope='session')
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = AsyncElasticsearch(
        hosts=f'http://{settings.elastic_host}' f':{str(settings.elastic_port)}'
    )
    await asyncio.sleep(1)
    await build_indexes(client, settings.all_indexes)
    yield client
    await remove_indexes(client, settings.all_indexes)
    await client.close()


class FixtureTypeElasticDataWriter(Protocol):
    async def __call__(self, data: list[dict[str, Any]], es_index: str) -> None:
        ...


@pytest.fixture()
def es_write_data(
    es_client: AsyncElasticsearch,
) -> FixtureTypeElasticDataWriter:
    async def inner(data: list[dict[str, Any]], es_index: str) -> None:
        try:
            await async_bulk(
                es_client, get_es_bulk_query(data, es_index, settings.es_id_field)
            )
        except BulkIndexError as e:
            logger.error(f'BulkIndexError: {e}')

    return inner
