import logging
from sqlite3 import Connection
from sqlite3 import Error as SqLiteError

import psycopg2
from configuration import DSL, LOG_FORMAT
from psycopg2.extensions import connection as _connection
from service import PostgresSaver, SQLiteExtractor, pg_conn_context, sl_conn_context

logging.basicConfig(
    filename='logs/logfile.log',
    level=logging.INFO,
    encoding='utf-8',
    datefmt='%d.%m.%y %H:%M:%S',
    format=LOG_FORMAT,
)


def load_from_sqlite(connection: Connection, pg_conn: _connection) -> None:
    """Основной метод загрузки данных из SQLite в Postgres"""
    try:
        postgres_saver = PostgresSaver(pg_conn)
        sqlite_extractor = SQLiteExtractor(connection)
        data = sqlite_extractor.extract_movies()
        postgres_saver.save_all_data(data)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    try:
        with (
            sl_conn_context('db.sqlite') as sqlite_conn,
            pg_conn_context(DSL) as pg_conn,
        ):
            load_from_sqlite(sqlite_conn, pg_conn)
    except SqLiteError as e:
        logging.error(f'Ошибка в подключении к БД sqlite: {e}')
    except psycopg2.DatabaseError as e:
        logging.error(f'Ошибка в подключении к БД postgresql: {e}')
