import uuid

from models.mixins import ConfigMixin


class Person(ConfigMixin):
    id: uuid.UUID
    name: str


class PersonFull(Person):
    film_ids: list[uuid.UUID]
