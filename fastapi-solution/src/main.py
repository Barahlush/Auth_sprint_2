from api.v1 import films, genres, persons
from core.config import elastic_settings, redis_settings, settings
from core.logger import get_logger
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis import asyncio as aioredis

logger = get_logger(__name__)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup() -> None:
    redis.redis = aioredis.from_url(
        f'redis://{redis_settings.host}:{redis_settings.port}'
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f'http://{elastic_settings.host}:{elastic_settings.port}']
    )


@app.on_event('shutdown')
async def shutdown() -> None:
    if redis.redis:
        await redis.redis.close()
    if elastic.es:
        await elastic.es.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
