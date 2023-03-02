
from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch:
    if not es:
        raise Exception('Elastic is not initialized yet.')
    return es
