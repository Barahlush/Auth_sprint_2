import logging

from aiobreaker import CircuitBreaker, CircuitBreakerListener
from httpx import RequestError, AsyncClient
from starlette.responses import RedirectResponse

from api.v1 import films, genres, persons
from core.config import elastic_settings, redis_settings, settings
from core.logger import get_logger
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, Response
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

auth_breaker = CircuitBreaker(fail_max=5)


@app.middleware('http')
async def add_process_time_header(request: Request):
    headers = request.headers
    base_url = 'http://' + settings.auth_url
    try:
        auth_answer = await send_circuit_request(f'{base_url}/auth', headers=dict(headers))
    except RequestError:
        return RedirectResponse(url=base_url, status_code=401)
    if auth_answer.status_code == 200:
        data = auth_answer.json()
        if 'user' in data['roles']:
            RedirectResponse(url=f'{base_url}/search?size=10', status_code=200)
        return RedirectResponse(url=f'{base_url}/register', status_code=403)
    return RedirectResponse(url=base_url, status_code=401)


class LogListener(CircuitBreakerListener):
    def state_change(self, breaker, old, new):
        logging.info(f'{old.state} -> {new.state}')


@auth_breaker
async def send_circuit_request(url: str, headers: dict):
    async with AsyncClient() as client:
        answer = await client.get(url, headers=headers)
        logging.info(answer)
        return answer
