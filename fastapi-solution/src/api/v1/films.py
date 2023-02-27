from typing import Sequence, Union

from fastapi import APIRouter, Depends, Query
from models.films import Film, FilmFull
from services.api_services import BaseService, get_film_service
from services.utils import CommonQueryParams, HTTPNotFoundException

router = APIRouter()


@router.get(
    '/',
    response_model=Sequence[Film],
    summary='Get Movies',
    description='Get list of movies with search and filters',
)
@router.get(
    '/search',
    response_model=Sequence[Film],
    summary='Search Movies',
    description='Get list of movies with search and filters',
)
async def film_list(
    genre: Union[str, None] = Query(
        default=None, alias='filter[genre]', description='Filter by genre uuid'
    ),
    writers: Union[str, None] = Query(
        default=None,
        alias='filter[writer]',
        description='Filter by writer (person) uuid',
    ),
    actors: Union[str, None] = Query(
        default=None, alias='filter[actor]', description='Filter by actor (person) uuid'
    ),
    directors: Union[str, None] = Query(
        default=None,
        alias='filter[director]',
        description='Filter by director (person) uuid',
    ),
    query: Union[str, None] = Query(
        default=None, description='Text for search by title'
    ),
    common: CommonQueryParams = Depends(CommonQueryParams),
    film_service: BaseService = Depends(get_film_service),
) -> Sequence[Film]:
    """Returns list of films by the parameters specified in the query."""
    films: Sequence[Film] | None = await film_service.get_items(
        sort=common.sort,
        size=common.size,
        page_num=common.page_num,
        genre=genre,
        writers=writers,
        actors=actors,
        directors=directors,
        query=query,
    )
    if not films:
        raise HTTPNotFoundException(detail='Films not found')
    return films


@router.get(
    '/{film_id}',
    response_model=FilmFull,
    summary='Get Movie',
    description='Get Movie by id with all the information',
)
async def film_details(
    film_id: str, film_service: BaseService = Depends(get_film_service)
) -> FilmFull:
    """Returns one film."""
    film = await film_service.get_by_id(film_id)  # type: ignore
    if not film:
        raise HTTPNotFoundException(detail='Film not found')
    return film
