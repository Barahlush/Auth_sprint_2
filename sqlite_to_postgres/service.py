import dataclasses
import sqlite3
from contextlib import contextmanager
from sqlite3 import Connection
from typing import Any, Dict, Generator, Iterator, List, Tuple

import psycopg2
from configuration import FIELD_TYPE, PACK_SIZE, TABLE_CLASS
from psycopg2 import Error as PostgresError
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_batch


@contextmanager
def sl_conn_context(db_path: str) -> Iterator[Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@contextmanager
def pg_conn_context(DSL: Dict[Any, Any]) -> Iterator[_connection]:
    conn = psycopg2.connect(**DSL, cursor_factory=DictCursor)
    yield conn
    conn.close()


class PostgresSaver:
    def __init__(self, pg_conn: _connection) -> None:
        self.pg_conn = pg_conn
        self.cursor = self.pg_conn.cursor()

    def save_all_data(self, data: Dict[Any, Any]) -> None:
        """Основной метод записи данных в Postgres."""
        self.truncate()
        for table in TABLE_CLASS:
            self.save_data(*self.sql_data_generator(data[table]))

    def truncate(self) -> None:
        """Метод для удаления старых данный перед записью."""
        try:
            for table in TABLE_CLASS:
                self.cursor.execute(f'TRUNCATE content.{table} CASCADE;')
            self.pg_conn.commit()
        except PostgresError as e:
            raise PostgresError('Ошибка при удалении данных из Postgres ' f'базы: {e}')

    def save_data(self, prepare_sql: str, sql: str, data: List[Any]) -> None:
        """Метод который непосредственно общается Postgres."""
        try:
            self.cursor.execute(prepare_sql)
            execute_batch(self.cursor, sql, data, PACK_SIZE)
            self.pg_conn.commit()
        except PostgresError as e:
            raise PostgresError(f'Ошибка при записи данных в Postgres: {e}')

    def fields_types_extractor(
        self, table: str
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        try:
            """Метод генерирует список полей
            с типами данных на основе указанной таблицы."""
            data_types = [
                FIELD_TYPE[field.name]
                for field in dataclasses.fields(TABLE_CLASS[table])
            ]
            fields = [field.name for field in dataclasses.fields(TABLE_CLASS[table])]
            nums_fields = [
                '$' + str(i + 1)
                for i in range(len(dataclasses.fields(TABLE_CLASS[table])))
            ]
            return data_types, fields, nums_fields
        except Exception as e:
            raise Exception(
                'Ошибка в генерации полей с типами данных для '
                f'работы с таблицей {table}: {e}'
            )

    def sql_data_generator(self, data: List[Any]) -> Tuple[str, str, List[Any]]:
        """Метод генерирует запросы для работы с указанной таблицей."""
        try:
            tb_name = str(data[0])
            types, fields, nums_fields = self.fields_types_extractor(tb_name)
            data_types = ', '.join(types)
            str_nums_fields = ', '.join(nums_fields)
            vars_list = ', '.join(['%s' for _ in range(len(nums_fields))])
            prepare_sql = (
                f'PREPARE {tb_name}_insert ({data_types}) '
                f'AS INSERT INTO content.{tb_name} '
                f'VALUES({str_nums_fields});'
            )
            execute_sql = f'EXECUTE {tb_name}_insert({vars_list});'
            data = [tuple([getattr(fw, field) for field in fields]) for fw in data]
            print(data[0])
            print(data[1])
            return prepare_sql, execute_sql, data
        except Exception as e:
            raise Exception(
                'Ошибка в подготовке запросов и данных для работы '
                f'с таблицей {tb_name}: {e}'
            )


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.curs = self.connection.cursor()

    def executor(self, sql: str) -> Generator[Any, Any, Any]:
        self.curs.execute(sql)
        while True:
            rows = self.curs.fetchmany(size=PACK_SIZE)
            if not rows:
                break
            yield from rows

    def extract_movies(self) -> Dict[Any, Any]:
        """Метод проходит по всем таблицам SQlite БД и укладывает данные в
        словарь со списками датаклассов."""
        try:
            dictionary = {}
            for key in TABLE_CLASS:
                dictionary[key] = self.extract_data_from(key)
            return dictionary
        except Exception as e:
            raise Exception(
                'Ошибка в работе скриализатора при составлении '
                f'SQL запроса к SQlite БД: {e}'
            )

    def fields_serializer(self, fields: List[Any]) -> str:
        """Метод преобразует список атрибутов Датакласса к списку полей БД."""
        try:
            for i in range(len(fields)):
                if fields[i] == 'created':
                    fields[i] = 'created_at AS created'
                if fields[i] == 'modified':
                    fields[i] = 'updated_at AS modified'
            return ', '.join(fields)
        except Exception as e:
            raise Exception(
                'Ошибка в работе сериализатора при составлении '
                f'SQL запроса к SQlite БД: {e}'
            )

    def extract_sql_generator(self, table: str) -> str:
        """Метод генерирует SQL код запроса к БД на основе названия таблицы."""
        try:
            fields = [field.name for field in dataclasses.fields(TABLE_CLASS[table])]
            fields_str = self.fields_serializer(fields)
            return f'SELECT {fields_str} FROM {table};'
        except Exception as e:
            raise Exception('Ошибка при генерации SQL запроса к ' f'SQlite БД: {e}')

    def extract_data_from(self, table: str) -> List[Any]:
        """Метод извлекает данны из БД и преобразует их в список."""
        try:
            sql = self.extract_sql_generator(table)
            return [TABLE_CLASS[table](**dict(_)) for _ in self.executor(sql)]
        except sqlite3.Error as e:
            raise sqlite3.Error(
                'Ошибка при извлечении данных из sqlite ' f'таблицы {table}: {e}'
            )
