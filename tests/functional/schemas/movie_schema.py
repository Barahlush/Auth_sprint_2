
from .genre_schema import FilmGenreValidation
from .mixin import PaginationValidation, UUIDValidation
from .person_schema import FilmPersonValidation


class ListFilmValidation(UUIDValidation):

    title: str
    imdb_rating: float | None = None


class DetailResponseFilm(ListFilmValidation):
    description: str | None = None
    genre: list[FilmGenreValidation] | None = []
    actors: list[FilmPersonValidation] | None = []
    writers: list[FilmPersonValidation] | None = []
    directors: list[FilmPersonValidation] | None = []


class FilmPaginationValidation(PaginationValidation):
    films: list[ListFilmValidation] = []
