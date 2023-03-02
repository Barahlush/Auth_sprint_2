import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации

# Настройки Redis

# Настройки Elasticsearch

# Корень проекта


class Settings(BaseSettings):
    cache_expired: int = Field(350, env='CACHE_EXPIRE_IN_SECONDS')
    film_body_params: list[str] = ['directors', 'genre', 'writers', 'actors']
    person_body_params: list[str] = ['film_ids']
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_name: str = Field('movies', env='PROJECT_NAME')
    auth_url: str = Field('127.0.0.1:5000', env='AUTH_URL')
    movies_url: str = Field('127.0.0.1:8000', env='MOVIES_URL')

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
