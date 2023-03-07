import os
from pathlib import Path

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Настройки Postgres
POSTGRES_DSL: dict[str, str | int] = {
    'dbname': os.environ.get('POSTGRES_DB', 'postgres'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'host': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
    'port': os.environ.get('POSTGRES_PORT', 5432),
}

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCHEMA_FOLDER = Path('etl_schema/')
