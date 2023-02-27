from typing import Optional
from uuid import UUID

from .mixin import UUIDValidation


class FilmPersonValidation(UUIDValidation):
    name: str


class DetailPersonValidation(FilmPersonValidation):
    film_ids: Optional[list[UUID]] = []
