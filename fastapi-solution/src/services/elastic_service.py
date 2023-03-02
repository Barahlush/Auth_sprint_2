from typing import Any

from core.backoff import backoff_function
from core.logger import get_logger
from elastic_transport import ConnectionError
from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError
from pydantic import BaseModel

from services.ancestors import SearchService
from services.utils import parse_params

logger = get_logger(__name__)


class ElasticService(SearchService):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    @backoff_function(ConnectionError)
    async def get_one(
        self, id: str, index: str, model: type[BaseModel]
    ) -> BaseModel | None:
        try:
            doc = await self.elastic.get(index=index, id=id)
            return model(**doc['_source'])
        except NotFoundError as error:
            logger.error(
                'Failed to read %s id=%s from Elastic.\n %s',
                index,
                id,
                error,
            )
        except Exception as error:
            logger.error(
                'Failed to read data from Elastic.\n %s',
                error,
            )
        return None

    @backoff_function(ConnectionError)
    async def get_several(
        self,
        index: str,
        model: type[BaseModel],
        query_params: list[str] | None,
        is_nested: bool = False,
        **kwargs: Any
    ) -> list[BaseModel]:
        try:
            body, params = parse_params(query_params, is_nested, **kwargs)
            docs = await self.elastic.search(
                index=index, query=body['query'], **params
            )
            return [model(**doc['_source']) for doc in docs['hits']['hits']]
        except NotFoundError as error:
            logger.error(
                'Failed to read persons from Elastic. Not Found. \n %s',
                error,
            )
        except BadRequestError as error:
            logger.error(
                'Failed to read data from Elastic. Bad request. \n %s',
                error,
            )
        except Exception as error:
            logger.error(
                'Failed to read data from Elastic. Unexpected error. \n %s',
                error,
            )
        return []
