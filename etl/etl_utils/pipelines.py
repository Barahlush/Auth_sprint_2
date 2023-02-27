from typing import Any, Generator, TypeVar

from config import REDIS_HOST, REDIS_PORT
from etl_utils.elastic_search_handlers import (
    ElasticSearchFilmTransformer,
    ElasticSearchGenreTransformer,
    ElasticSearchLoader,
    ElasticSearchPersonTransformer,
)
from etl_utils.postgres_handlers import (
    PostgresFilmEnricher,
    PostgresFilmMerger,
    PostgresFilmProducer,
    PostgresGenreProducer,
    PostgresPersonProducer,
    PostgresProducer,
)
from etl_utils.state import RedisStorage, State
from psycopg2.extras import DictRow
from redis import Redis

ElasticSearchTransformer = TypeVar(
    'ElasticSearchTransformer',
    ElasticSearchGenreTransformer,
    ElasticSearchFilmTransformer,
    ElasticSearchPersonTransformer,
)


class BasePipeline:
    """Base ETL pipeline class.
    Implements extraction of updated entities from Postgres (PostgresProducer),
    selecting all required for ElasticSearch data about them
    (PostgresFilmEnricher, PostgresFilmMerger), validating and transforming data
    for ElasticSearch (ElasticSearchDataTransformer) and uploading data
    to ElasticSearch (ElasticSearchLoader).
    """

    def __init__(
        self,
        redis_key: str,
        loader_batch_size: int = 128,
    ):
        """
        Args:
            redis_key (str]):
                key for Redis state storage.
            loader_batch_size (int, optional):
                batch size for object uploading to ElasticSearch. Defaults to 128.
        """
        self.state = State(RedisStorage(Redis(REDIS_HOST, REDIS_PORT), redis_key))
        self._es_transformer: ElasticSearchTransformer = None  # type: ignore
        self._es_loader: ElasticSearchLoader | None = None
        self._producer: PostgresProducer | None = None
        self._merger: PostgresFilmMerger | None = None
        self._enricher: PostgresFilmEnricher | None = None

    @property
    def es_transformer(self) -> ElasticSearchTransformer:
        if not self._es_transformer:
            raise NotImplementedError
        return self._es_transformer

    @property
    def es_loader(self) -> ElasticSearchLoader:
        if not self._es_loader:
            raise NotImplementedError
        return self._es_loader

    @property
    def producer(self) -> PostgresProducer:
        if not self._producer:
            raise NotImplementedError
        return self._producer

    @property
    def merger(self) -> PostgresFilmMerger | None:
        return self._merger

    @property
    def enricher(self) -> PostgresFilmEnricher | None:
        return self._enricher

    def extract(self) -> Generator[list[DictRow], None, None]:
        """Extracts all the data required by ElasticSearch scheme from Postgres.

        Yields:
            list[DictRow]:
                batch of Postgres DictRows with all the data required in ElasticSearch.
        """
        for batch in self.producer.produce_batch():
            if self.enricher and self.merger:
                for enriched_batch in self.enricher.enrich_batch(batch):
                    yield self.merger.merge_batch(enriched_batch)
            elif self.merger:
                yield self.merger.merge_batch(batch)
            else:
                yield batch

    def transform(
        self, producer_data_generator: Generator[list[DictRow], None, None]
    ) -> Generator[dict[str, Any], None, None]:
        """Transforms raw data from Postgres Producer into ElasticSearch format.

        Args:
            producer_data_generator (Generator[list[DictRow], None, None]):
                generator of Postgres DictRows with producer data

        Yields:
            dict[str, Any]:
                dict with fields from ElasticSearch index mapping.
        """
        for producer_data_batch in producer_data_generator:
            yield from self.es_transformer.transform(producer_data_batch)

    def load(self, prepared_data: Generator[dict[str, Any], None, None]) -> None:
        """Loads transformed data to ElasticSearch.

        Args:
            prepared_data (Generator[dict[str, Any], None, None]):
                generator of dicts from `transform` function in ElasticSearch index format.
        """
        self.es_loader.upload(prepared_data)

    def run(self) -> None:
        """Runs the whole ETL pipeline"""
        self.load(self.transform(self.extract()))


class GenreETLPipeline(BasePipeline):
    def __init__(
        self,
        redis_key: str,
        producer_batch_size: int = 128,
        loader_batch_size: int = 128,
    ):
        """
        Args:
            redis_key (str]):
                key for Redis state storage.
            producer_batch_size (int, optional):
                batch size for batch producer to extract updated entities. Defaults to 128.
            loader_batch_size (int, optional):
                batch size for object uploading to ElasticSearch. Defaults to 128.
        """
        super().__init__(redis_key, loader_batch_size)
        self._es_loader = ElasticSearchLoader(loader_batch_size, 'genres')
        self._es_transformer = ElasticSearchGenreTransformer(self.state)
        self._producer = PostgresGenreProducer(
            self.state, producer_batch_size, 'et_genre_producer'
        )


class PersonETLPipeline(BasePipeline):
    def __init__(
        self,
        redis_key: str,
        producer_batch_size: int = 128,
        loader_batch_size: int = 128,
    ):
        """
        Args:
            redis_key (str]):
                key for Redis state storage.
            producer_batch_size (int, optional):
                batch size for batch producer to extract updated entities. Defaults to 128.
            loader_batch_size (int, optional):
                batch size for object uploading to ElasticSearch. Defaults to 128.
        """
        super().__init__(redis_key, loader_batch_size)
        self._es_loader = ElasticSearchLoader(loader_batch_size, 'persons')
        self._es_transformer = ElasticSearchPersonTransformer(self.state)
        self._producer = PostgresPersonProducer(
            self.state, producer_batch_size, 'et_person_producer'
        )


class FilmETLPipeline(BasePipeline):
    def __init__(
        self,
        redis_key: str,
        table_name: str,
        enrich: bool = False,
        enricher_batch_size: int = 128,
        producer_batch_size: int = 128,
        loader_batch_size: int = 128,
    ):
        """
        Args:
            redis_key (str):
                key for Redis state storage.
            table_name (str):
                table name to check filmwork updates
            enrich (bool):
                if True,
            producer_batch_size (int, optional):
                batch size for batch producer to extract updated entities. Defaults to 128.
            enrich_batch_size (int, optional):
                batch size for batch enricher to add data to updated entities. Defaults to 128.
            loader_batch_size (int, optional):
                batch size for object uploading to ElasticSearch. Defaults to 128.
        """
        super().__init__(redis_key, loader_batch_size)
        self._es_loader = ElasticSearchLoader(loader_batch_size, 'movies')
        self._es_transformer = ElasticSearchFilmTransformer(self.state)
        self._producer = PostgresFilmProducer(
            self.state, producer_batch_size, 'et_person_producer', table_name
        )
        self._merger = PostgresFilmMerger()
        if enrich:
            self._enricher = PostgresFilmEnricher(
                self.state, enricher_batch_size, table_name
            )
