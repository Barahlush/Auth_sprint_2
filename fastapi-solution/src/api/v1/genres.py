from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query
from models.genres import Genre, GenreFull
from services.api_services import BaseService, get_genre_service
from services.utils import CommonQueryParams, HTTPNotFoundException

router = APIRouter()


@router.get(
    '/',
    response_model=Sequence[Genre],
    summary='Get Genres',
    description='Get list of Genres with search and filters',
)
async def genre_list(
    query: str
    | None = Query(default=None, description='Text for search by genres'),
    common: CommonQueryParams = Depends(CommonQueryParams),
    genre_service: BaseService = Depends(get_genre_service),
) -> Sequence[Genre]:
    """Returns list of Genres by the parameters specified in the query."""
    genres: Sequence[Genre] | None = await genre_service.get_items(
        sort=common.sort,
        size=common.size,
        page_num=common.page_num,
        query=query,
    )
    if not genres:
        raise HTTPNotFoundException(detail='Genres not found')
    return genres


@router.get(
    '/{genre_id}',
    response_model=GenreFull,
    summary='Get Genre',
    description='Get Genre by id with all the information',
)
async def genre_details(
    genre_id: str, genre_service: BaseService = Depends(get_genre_service)
) -> GenreFull:
    """Returns one genre."""
    genre: GenreFull | None = await genre_service.get_by_id(genre_id)  # type: ignore
    if not genre:
        raise HTTPNotFoundException(detail='Genre not found')
    return genre
