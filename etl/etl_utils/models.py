from uuid import UUID

from pydantic import BaseModel, Field


class NamedEntity(BaseModel):
    """Used for genre/person entities."""

    id: UUID
    name: str

    class Config:
        frozen = True

    def __str__(self) -> str:
        return self.name


class Filmwork(BaseModel):
    id: UUID
    elastic_id: UUID = Field(alias='_id')
    imdb_rating: float | None
    genres: list[NamedEntity]
    title: str
    description: str | None
    director: list[NamedEntity]
    actors: list[NamedEntity]
    writers: list[NamedEntity]


class Genre(BaseModel):
    id: UUID
    elastic_id: UUID = Field(alias='_id')
    name: str
    description: str | None


class Person(BaseModel):
    id: UUID
    elastic_id: UUID = Field(alias='_id')
    name: str
    film_ids: list[UUID]
