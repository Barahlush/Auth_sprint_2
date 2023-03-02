import json
from collections.abc import Generator, Iterator
from copy import deepcopy
from itertools import groupby
from operator import attrgetter
from typing import Any, cast
from uuid import UUID

from config import ELASTIC_HOST, ELASTIC_PORT, SCHEMA_FOLDER
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from elasticsearch.helpers import streaming_bulk
from psycopg2.extras import DictRow

from etl_utils.backoff import backoff_function
from etl_utils.loggers import setup_logger
from etl_utils.models import Filmwork, Genre, NamedEntity, Person
from etl_utils.state import State, StatefulMixin

logger = setup_logger(__name__)


class ElasticSearchLoader:
    def __init__(self, batch_size: int, index_name: str):
        self.index_name = index_name
        self.batch_size = batch_size
        self.es_client = Elasticsearch(f'http://{ELASTIC_HOST}:{ELASTIC_PORT}')
        logger.info(
            'Connecting to ElasticSearch...\nHost: http://%s:%s',
            ELASTIC_HOST,
            ELASTIC_PORT,
        )

    @backoff_function(TransportError)
    def upload(
        self, data_generator: Generator[dict[str, Any], None, None]
    ) -> None:
        """Uploads data to ElasticSearch using `streaming_bulk`.

        Args:
            data_generator (Generator[dict[str, Any], None, None]):
                generator of dicts with data as in index scheme of ElasticSearch.
        """
        if not self.es_client.indices.exists(index=self.index_name):
            self.create_index()
        successes: int = 0
        errors = []
        for ok, action in streaming_bulk(
            client=self.es_client,
            chunk_size=self.batch_size,
            index=self.index_name,
            actions=data_generator,
        ):
            successes += ok
            if not ok:
                errors.append(action)
        logger.info(
            '%d documents uploaded to ES. %d errors.', successes, len(errors)
        )

    def create_index(self) -> None:
        """Creates an index in ElasticSearch if one isn't already there."""
        with open(
            SCHEMA_FOLDER / f'{self.index_name}_index_mappings.json'
        ) as mappings_file:
            mappings = json.load(mappings_file)
        with open(
            SCHEMA_FOLDER / f'{self.index_name}_index_settings.json'
        ) as settings_file:
            settings = json.load(settings_file)

        response = self.es_client.indices.create(
            index=self.index_name, mappings=mappings, settings=settings
        )
        logger.info('Index created. %s', response.body)


class ElasticSearchFilmTransformer(StatefulMixin):
    def __init__(self, state: State):
        super().__init__(state, 'es_loader_last_updated_films')

    def transform(
        self, merged_data: list[DictRow]
    ) -> Generator[dict[str, Any], None, None]:

        """Transforms raw merged filmwork data from Postgres into dicts
        which could be loaded to ElasticSearch.

        Args:
            merged_data (list[DictRow]):
                merged data from Postgres.

        Yields:
            dict[str, Any]:
                dict in the format of Elastic Search `movies` index.
        """

        groups: Iterator[tuple[UUID, Iterator[DictRow]]] = groupby(
            sorted(merged_data, key=lambda row: cast(UUID, row['fw_id'])),
            lambda row: cast(UUID, row['fw_id']),
        )
        filmworks = [
            dict(list(next(group).items())[:5])  # type: ignore
            for fw_id, group in deepcopy(groups)
        ]

        def get_unique_persons(
            groups: Iterator[tuple[UUID, Iterator[DictRow]]], role: str
        ) -> list[list[NamedEntity]]:
            """Extracts and groups all persons of the same `role` for each film in `groups`.

            Args:
                groups (Iterator[tuple[UUID, Iterator[DictRow]]]):
                    result of groupby on raw merged data from Postgres.
                role (str):
                    role to extract.

            Returns:
                list[list[NamedEntity]]:
                    list containing lists of persons with the `role` for each film in `groups`.
            """
            return [
                sorted(
                    {
                        NamedEntity(name=row['p_full_name'], id=row['p_id'])
                        for row in group
                        if row['p_role'] == role
                    },
                    key=attrgetter('name'),
                )
                for fw_id, group in deepcopy(groups)
            ]

        genres = [
            sorted(
                {
                    NamedEntity(id=row['g_id'], name=row['g_name'])
                    for row in group
                },
                key=attrgetter('name'),
            )
            for fw_id, group in deepcopy(groups)
        ]
        actors = get_unique_persons(groups, 'AC')
        writers = get_unique_persons(groups, 'WR')
        directors = get_unique_persons(groups, 'DR')

        for i in range(len(filmworks)):
            yield Filmwork(
                id=filmworks[i]['fw_id'],
                _id=filmworks[i]['fw_id'],
                imdb_rating=filmworks[i]['rating'],
                title=filmworks[i]['title'],
                description=filmworks[i]['description'],
                genres=genres[i],
                director=directors[i],
                actors=actors[i],
                writers=writers[i],
            ).dict(by_alias=True)


class ElasticSearchGenreTransformer(StatefulMixin):
    def __init__(self, state: State):
        super().__init__(state, 'es_loader_last_updated_genres')

    def transform(
        self, genres_data: list[DictRow]
    ) -> Generator[dict[str, Any], None, None]:

        """Transforms genre data from Postgres into dicts
        which could be loaded to ElasticSearch.

        Args:
            genres_data (list[DictRow]):
                data from Postgres.

        Yields:
            dict[str, Any]:
                dict in the format of Elastic Search `genres` index.
        """
        for genre in genres_data:
            yield Genre(
                id=str(genre['id']),
                _id=str(genre['id']),
                name=genre['name'],
                description=genre['description'],
            ).dict(by_alias=True)


class ElasticSearchPersonTransformer(StatefulMixin):
    def __init__(self, state: State):
        super().__init__(state, 'es_loader_last_updated_persons')

    def transform(
        self, persons_data: list[DictRow]
    ) -> Generator[dict[str, Any], None, None]:

        """Transforms person data from Postgres into dicts
        which could be loaded to ElasticSearch.

        Args:
            persons_data (list[DictRow]):
                data from Postgres.

        Yields:
            dict[str, Any]:
                dict in the format of Elastic Search `persons` index.
        """
        groups: Iterator[tuple[UUID, Iterator[DictRow]]] = groupby(
            sorted(persons_data, key=lambda row: cast(UUID, row['p_id'])),
            lambda row: cast(UUID, row['p_id']),
        )
        for p_id, group in groups:
            film_ids = []
            for person_row in group:
                film_ids.append(person_row['f_id'])
            full_name = person_row['p_full_name']
            action = Person(
                id=str(p_id),
                _id=str(p_id),
                name=full_name,
                film_ids=[str(i) for i in film_ids],
            ).dict(by_alias=True)
            yield action
