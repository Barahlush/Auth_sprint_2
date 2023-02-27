from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    fastapi_host = Field('fastapi', env='API_HOST')
    fastapi_port = Field(80, env='API_PORT')
    elastic_host: str = Field('elastic', env='ELASTIC_HOST')
    elastic_port: int = Field(9200, env='ELASTIC_PORT')
    redis_host: str = Field('redis', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
    person_index: str = 'persons'
    genre_index: str = 'genres'
    movies_index: str = 'movies'
    all_indexes: list[str] = ['movies', 'genres', 'persons']
    es_id_field: str = 'id'

    class Config:
        env_file = './.env'
        env_file_encoding = 'utf-8'


settings = Settings()
