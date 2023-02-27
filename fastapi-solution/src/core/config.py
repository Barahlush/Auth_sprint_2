import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings, Field

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
# PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
# REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
# REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
# ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
# ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Корень проекта
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    cache_expired: int = Field(350, env='CACHE_EXPIRE_IN_SECONDS')
    film_body_params: list[str] = ['directors', 'genre', 'writers', 'actors']
    person_body_params: list[str] = ['film_ids']
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_name: str = Field('movies', env='PROJECT_NAME')

    class Config:
        env_file = '../../../.env'
        env_file_encoding = 'utf-8'


class RedisSettings(BaseSettings):
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')

    class Config:
        env_file = '../../../.env'
        env_file_encoding = 'utf-8'


class ElasticSettings(BaseSettings):
    host: str = Field('127.0.0.1', env='ELASTIC_HOST')
    port: int = Field(9200, env='ELASTIC_PORT')

    class Config:
        env_file = '../../../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
redis_settings = RedisSettings()
elastic_settings = ElasticSettings()
