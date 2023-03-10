from .mixin import UUIDValidation


class FilmGenreValidation(UUIDValidation):
    name: str
    description: str | None
