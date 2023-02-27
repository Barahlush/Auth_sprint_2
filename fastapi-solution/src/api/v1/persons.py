from typing import Sequence, Union

from fastapi import APIRouter, Depends, Query
from models.persons import PersonFull
from services.api_services import BaseService, get_person_service
from services.utils import CommonQueryParams, HTTPNotFoundException

router = APIRouter()


@router.get(
    '/',
    response_model=Sequence[PersonFull],
    summary='Get Persons',
    description='Get list of Persons with search and filters',
)
@router.get(
    '/search',
    response_model=Sequence[PersonFull],
    summary='Search Persons',
    description='Get list of Persons with search and filters',
)
async def person_list(
    film_ids: Union[str, None] = Query(default=None, alias='filter[film_ids]'),
    query: Union[str, None] = Query(
        default=None, description='Text for search by persons'
    ),
    common: CommonQueryParams = Depends(CommonQueryParams),
    person_service: BaseService = Depends(get_person_service),
) -> Sequence[PersonFull]:
    """Returns list of persons by the parameters specified in the query."""
    persons: Sequence[PersonFull] | None = await person_service.get_items(
        sort=common.sort,
        size=common.size,
        film_ids=film_ids,
        page_num=common.page_num,
        query=query,
    )
    if not persons:
        raise HTTPNotFoundException(detail='Persons not found')
    return persons


@router.get(
    '/{person_id}',
    response_model=PersonFull,
    summary='Get Person',
    description='Get Person by id with all the information',
)
async def person_details(
    person_id: str, person_service: BaseService = Depends(get_person_service)
) -> PersonFull:
    """Returns one person."""
    person: PersonFull | None = await person_service.get_by_id(person_id)  # type: ignore
    if not person:
        raise HTTPNotFoundException(detail='Person not found')
    return person
