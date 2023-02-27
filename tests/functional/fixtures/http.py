from typing import Any, AsyncGenerator, Protocol

import aiohttp
import pytest
import pytest_asyncio
from pydantic import BaseModel
from settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class HTTPResponse(BaseModel):
    body: list[dict[str, Any]] | dict[str, Any] | None
    headers: dict[str, Any] | None
    status: int


@pytest_asyncio.fixture(scope='session')
async def http_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    session = aiohttp.ClientSession()
    yield session
    await session.close()


class FixtureTypeGetRequestMaker(Protocol):
    async def __call__(self, endpoint: str, params: dict[str, Any]) -> HTTPResponse:
        ...


@pytest.fixture
def make_get_request(http_session: aiohttp.ClientSession) -> FixtureTypeGetRequestMaker:
    async def inner(endpoint: str, params: dict[str, Any]) -> HTTPResponse:
        url = f'http://{settings.fastapi_host}:{str(settings.fastapi_port)}/api/v1/{endpoint}'
        response = await http_session.get(url, params=params)
        response_json = await response.json()
        return HTTPResponse(
            body=response_json,
            headers=response.headers,
            status=response.status,
        )

    return inner
