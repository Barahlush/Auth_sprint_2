from typing import Any, AsyncGenerator

from elasticsearch import AsyncElasticsearch
from es_index import film_work_schema, genre_schema, person_schema, schema_template
from utils.logger import get_logger

logger = get_logger(__name__)

SCHEMAS: dict[str, Any] = {
    'settings': schema_template.INDEX_BODY['settings'],
    'movies': film_work_schema.INDEX_BODY['mappings'],
    'genres': genre_schema.INDEX_BODY['mappings'],
    'persons': person_schema.INDEX_BODY['mappings'],
}


async def get_es_bulk_query(
    row_data: list[dict[str, Any]], index: str, id: str
) -> AsyncGenerator[dict[str, Any], None]:
    for obj in row_data:
        yield {'_index': index, '_id': obj.get(id), '_source': {**obj}}


async def remove_indexes(client: AsyncElasticsearch, indexes: list[str]) -> None:
    for index in indexes:
        try:
            await client.indices.delete(index=index)
        except Exception as e:
            logger.error(f'Error whie delete index "{index}" from Elasticsearch: {e}')


async def build_indexes(client: AsyncElasticsearch, indexes: list[str]) -> None:
    for index in indexes:
        try:
            await client.indices.create(
                index=index, settings=SCHEMAS['settings'], mappings=SCHEMAS[index]
            )
        except Exception as e:
            logger.error(f'Error whie create index "{index}" Elasticsearch: {e}')
