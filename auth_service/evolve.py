import peeweedbevolve

from src.v1.db.postgres import db
from src.v1.core.config import POSTGRES_CONFIG

if __name__ == '__main__':
    db.init(**dict(POSTGRES_CONFIG))
    db.evolve()
