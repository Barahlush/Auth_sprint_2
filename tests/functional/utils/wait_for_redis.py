from redis import ConnectionError, from_url
from settings import settings
from utils.backoff import backoff_function


@backoff_function(ConnectionError, AssertionError)  # type: ignore
def check_redis_exists(redis_client) -> None:
    assert redis_client.ping()


if __name__ == '__main__':
    redis_client = from_url(f'redis://{settings.redis_host}:{settings.redis_port}')
    check_redis_exists(redis_client)
