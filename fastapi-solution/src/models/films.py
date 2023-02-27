import uuid

from models.genres import Genre
from models.mixins import ConfigMixin
from models.persons import Person


class Film(ConfigMixin):
    id: uuid.UUID
    title: str
    description: str | None


class FilmFull(Film):
    imdb_rating: float | None
    genres: list[Genre] | None
    actors: list[Person] | None
    writers: list[Person] | None
    director: list[Person] | None
