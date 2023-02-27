import os

from dotenv import load_dotenv
from models_data import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork

load_dotenv()

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d ' '- %(message)s'
DSL = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
}
PACK_SIZE = 1000
TABLE_CLASS = {
    'film_work': Filmwork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmwork,
    'person_film_work': PersonFilmwork,
}
FIELD_TYPE = {
    'title': 'text',
    'description': 'text',
    'name': 'text',
    'type': 'text',
    'role': 'text',
    'full_name': 'text',
    'file_path': 'text',
    'rating': 'float',
    'id': 'uuid',
    'film_work_id': 'uuid',
    'genre_id': 'uuid',
    'person_id': 'uuid',
    'creation_date': 'date',
    'created_at': 'timestamp',
    'updated_at': 'timestamp',
}
