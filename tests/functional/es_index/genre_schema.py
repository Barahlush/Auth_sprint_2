from typing import Any

INDEX_BODY: dict[str, Any] = {
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {'type': 'keyword'},
            'name': {'type': 'keyword'},
            'description': {'type': 'text', 'analyzer': 'ru_en'},
        },
    },
}
