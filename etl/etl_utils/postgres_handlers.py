from contextlib import closing
from datetime import datetime
from typing import Generator

import psycopg2
import psycopg2.sql as sql
from config import POSTGRES_DSL
from etl_utils.backoff import backoff_function, backoff_generator
from etl_utils.loggers import setup_logger
from etl_utils.state import State, StatefulMixin
from psycopg2.extras import DictCursor, DictRow

logger = setup_logger(__file__)


class PostgresProducer(StatefulMixin):
    def __init__(
        self, query: sql.SQL | sql.Composed, state: State, batch_size: int, name: str
    ):
        super().__init__(state, f'{name}_last_modified')
        self.batch_size = batch_size
        self.query = query

    @backoff_generator(psycopg2.InterfaceError, psycopg2.OperationalError)
    def produce_batch(self) -> Generator[list[DictRow], None, None]:
        """Extracts all entities updated after specific time, saved in the state.

        Yields:
            list[DictRow]:
                batch of (id, updated_at) DictRows from arbitary table.
        """
        with closing(psycopg2.connect(**POSTGRES_DSL)) as conn:  # type: ignore
            with closing(conn.cursor(cursor_factory=DictCursor)) as cur:
                updated_after = self.get_last_modified()
                cur.execute(self.query, (updated_after,))
                while batch := cur.fetchmany(self.batch_size):
                    yield batch
                    self.set_last_modified(batch[-1]['updated_at'])


class PostgresPersonProducer(PostgresProducer):
    def __init__(self, state: State, batch_size: int, name: str):
        query = sql.SQL(
            '''
            SELECT
                p.id as p_id,
                p.full_name as p_full_name,
                pfw.film_work_id as f_id,
                p.updated_at
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
            WHERE p.updated_at > %s
            ORDER BY p.updated_at;'''
        )
        super().__init__(query, state, batch_size, name)


class PostgresGenreProducer(PostgresProducer):
    def __init__(self, state: State, batch_size: int, name: str):
        query = sql.SQL(
            '''
            SELECT
                id,
                name,
                description,
                updated_at
            FROM content.genre
            WHERE updated_at > %s
            ORDER BY updated_at;'''
        )
        super().__init__(query, state, batch_size, name)


class PostgresFilmProducer(PostgresProducer):
    def __init__(self, state: State, batch_size: int, name: str, table: str):
        self.table = table
        query = sql.SQL(
            '''
            SELECT id, updated_at
            FROM {}
            WHERE updated_at > %s
            ORDER BY updated_at;'''
        ).format(sql.Identifier('content', table))
        super().__init__(query, state, batch_size, name)


class PostgresFilmEnricher(StatefulMixin):
    def __init__(self, state: State, batch_size: int, table: str):
        super().__init__(state, f'{table}_enricher_last_modified')
        self.table = table
        self.batch_size = batch_size
        self.query = sql.SQL(
            '''
            SELECT fw.id, fw.updated_at
            FROM content.film_work fw
            LEFT JOIN {} produced ON produced.film_work_id = fw.id
            WHERE {} IN %s AND fw.updated_at > %s
            ORDER BY fw.updated_at;'''
        ).format(
            sql.Identifier('content', f'{table}_film_work'),
            sql.Identifier(f'{table}_id'),
        )

    @backoff_generator(psycopg2.InterfaceError, psycopg2.OperationalError)
    def enrich_batch(
        self, batch: list[DictRow]
    ) -> Generator[list[DictRow], None, None]:
        """Extracts all filmworks associated with entities in the batch
            if these filmworks were updated after specific time, saved in the state.

        Args:
            batch: list[DictRow]:
                list of (id, updated_at) DictRows form arbitary table.
        Yields:
            list[DictRow]:
                batch of (id, updated_at) DictRows from `film_work` table.
        """
        with closing(psycopg2.connect(**POSTGRES_DSL)) as conn:  # type: ignore
            with closing(conn.cursor(cursor_factory=DictCursor)) as cur:
                updated_after = self.get_last_modified()
                cur.execute(
                    self.query, (tuple(row['id'] for row in batch), updated_after)
                )
                while batch := cur.fetchmany(self.batch_size):
                    self.set_last_modified(batch[-1]['updated_at'])
                    yield batch
                self.set_last_modified(datetime.min)


class PostgresFilmMerger:
    def __init__(self) -> None:
        self.query = sql.SQL(
            '''
            SELECT
                fw.id as fw_id,
                fw.title,
                fw.description,
                fw.rating,
                fw.type,
                fw.created_at,
                fw.updated_at,
                pfw.role as p_role,
                p.id as p_id,
                p.full_name as p_full_name,
                g.name as g_name,
                g.id as g_id
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN %s;'''
        )

    @backoff_function(psycopg2.InterfaceError, psycopg2.OperationalError)
    def merge_batch(self, batch: list[DictRow]) -> list[DictRow]:
        """Extracts neccessary for ElasticSearch data
            associated with all the filmworks in the batch.

        Returns:
            list[DictRow]:
                batch of DictRows. Contains many DictRows per one filmwork.
        """
        with closing(psycopg2.connect(**POSTGRES_DSL)) as conn:  # type: ignore
            with closing(conn.cursor(cursor_factory=DictCursor)) as cur:
                cur.execute(self.query, (tuple(row['id'] for row in batch),))
                return cur.fetchall()  # type: ignore
