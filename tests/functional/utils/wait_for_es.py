import os
import sys

from elastic_transport import ConnectionError
from elasticsearch import Elasticsearch
from settings import settings
from utils.backoff import backoff_function
from utils.logger import get_logger

logger = get_logger(__name__)
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


@backoff_function(ConnectionError, AssertionError)
def check_es_exists(es_client: Elasticsearch) -> None:
    assert es_client.ping()


if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=f'http://{settings.elastic_host}:{str(settings.elastic_port)}'
    )
    check_es_exists(es_client)
