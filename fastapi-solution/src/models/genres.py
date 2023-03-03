import uuid

from models.mixins import ConfigMixin


class Genre(ConfigMixin):
    id: uuid.UUID
    name: str


class GenreFull(Genre):
    description: str | None
