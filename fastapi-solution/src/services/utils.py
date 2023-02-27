from http import HTTPStatus
from typing import Any, Dict, Optional, TypeVar

from core.logger import get_logger
from fastapi import HTTPException, Query
from pydantic import BaseModel

logger = get_logger(__name__)

ModelType = TypeVar('ModelType', bound=BaseModel)
BulkModelType = TypeVar('BulkModelType', bound=BaseModel)


def get_order_type(sort: str) -> str | None:
    """Sort string generator for elastic request."""
    try:
        if sort.startswith('-'):
            return f'{sort[1:]}:desc'
        return f'{sort}:asc'
    except Exception:
        logger.error('Error while generation sort string')
    return None


def parse_params(
    param_list: list[str] | None = None,
    nested_filter_params: bool = False,
    **kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    body_list = []
    params = {}
    if sort := kwargs.get('sort', None):
        params['sort'] = get_order_type(sort)

    if page_size := kwargs.get('size', None):
        params['size'] = page_size

    if page_num := kwargs.get('page_num', None):
        if not page_size:
            page_size = 10
        params['from'] = (page_num * page_size) - page_size

    if param_list:
        filters = {}
        for body_param in param_list:
            if item := kwargs.get(body_param, None):
                filters[body_param] = item
        for key in filters:
            match_key = f'{key}.id' if nested_filter_params else f'{key}'
            body_list.append(
                {
                    'match': {
                        match_key: str(filters[key]),
                    }
                }
            )
    if query := kwargs.get('query', None):
        body_list.append({'query_string': {'query': query}})
    body = {'query': {'bool': {'must': body_list}}}
    return body, params


class CommonQueryParams:
    def __init__(
        self,
        sort: str | None = Query(default=None, description='Sort by current param'),
        size: int
        | None = Query(
            default=None, alias='page[size]', description='Items per page', ge=0
        ),
        page_num: int
        | None = Query(
            default=None, alias='page[number]', description='Number of page', ge=0
        ),
    ):
        self.sort = sort
        self.size = size
        self.page_num = page_num


class HTTPNotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = HTTPStatus.NOT_FOUND,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
