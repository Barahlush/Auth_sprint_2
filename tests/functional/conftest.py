import asyncio
from glob import glob
from typing import Generator

import pytest
from utils.logger import get_logger
from utils.test_utils import refactor

logger = get_logger(__name__)

pytest_plugins = [refactor(fixture) for fixture in glob('*/fixtures/*.py')]


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.error('Event loop RuntimeError')
    yield loop
    loop.close()
