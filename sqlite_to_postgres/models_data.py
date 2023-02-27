import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Filmwork:
    title: str
    description: str
    creation_date: str
    type: str
    file_path: str
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return 'film_work'


@dataclass
class Genre:
    name: str
    description: str
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return 'genre'


@dataclass
class GenreFilmwork:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime = field(default=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return 'genre_film_work'


@dataclass
class Person:
    full_name: str
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return 'person'


@dataclass
class PersonFilmwork:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime = field(default=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return 'person_film_work'
