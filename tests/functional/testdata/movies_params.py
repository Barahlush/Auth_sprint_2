from http import HTTPStatus
from typing import Any

film_search_params: list[tuple[str, dict[str, Any], HTTPStatus]] = [
    ('films/search/', {'query': 'Star'}, HTTPStatus.OK),
    ('films/search/', {'query': 'Ptricluchenia Shurika'}, HTTPStatus.NOT_FOUND),
    ('films/search/', {'query': 'Star', 'page[number]': 2}, HTTPStatus.OK),
    (
        'films/search/',
        {'query': 'Star', 'page[number]': 2, 'page[size]': 3},
        HTTPStatus.OK,
    ),
    (
        'films/search/',
        {'query': 'Star', 'page[number]': 400, 'page[size]': 3},
        HTTPStatus.NOT_FOUND,
    ),
    (
        'films/search/',
        {'query': 'Star', 'page[number]': -1},
        HTTPStatus.UNPROCESSABLE_ENTITY,
    ),
    (
        'films/search/',
        {'query': 'Star', 'page[size]': -1},
        HTTPStatus.UNPROCESSABLE_ENTITY,
    ),
    ('films/search/', {'query': 'Star', 'sort': 'imdb_rating'}, HTTPStatus.OK),
    ('films/search/', {'query': 'Star', 'sort': '-imdb_rating'}, HTTPStatus.OK),
    ('films/search/', {'query': 'Star', 'sort': 'test'}, HTTPStatus.NOT_FOUND),
    (
        'films',
        {
            'query': 'Bright',
            'page[number]': 1,
            'page[size]': 10,
            'sort': '-imdb_rating',
            'filter[genre]': 'Drama',
        },
        HTTPStatus.OK,
    ),
]

film_list_params: list[tuple[str, dict[str, Any], HTTPStatus]] = [
    ('films', {}, HTTPStatus.OK),
    ('films', {'page[number]': 2, 'page[size]': 1}, HTTPStatus.OK),
    ('films', {'sort': 'imdb_rating'}, HTTPStatus.OK),
    ('films', {'sort': '-imdb_rating'}, HTTPStatus.OK),
    ('films', {'sort': 'test'}, HTTPStatus.NOT_FOUND),
    ('films', {'filter[genre]': 'Drama'}, HTTPStatus.OK),
]
