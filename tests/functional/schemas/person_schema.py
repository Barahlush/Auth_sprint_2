from uuid import UUID

from .mixin import UUIDValidation


class FilmPersonValidation(UUIDValidation):
    name: str


class DetailPersonValidation(FilmPersonValidation):
    film_ids: list[UUID] | None = []
