from typing import Any

INDEX_BODY: dict[str, Any] = {
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {'type': 'keyword'},
            'name': {
                'type': 'text',
                'analyzer': 'ru_en',
                'fields': {'raw': {'type': 'keyword'}},
            },
            'film_ids': {'type': 'keyword'},
        },
    },
}
