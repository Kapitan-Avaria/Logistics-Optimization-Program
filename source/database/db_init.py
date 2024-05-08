from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
engine = None


def db_init(db_path: Path):
    global engine
    is_empty = False

    if not db_path.parent.exists():
        raise Exception("You need to set db file name")

    engine = create_engine(f"sqlite+pysqlite:///{db_path}")

    if not database_exists(engine.url):
        create_database(engine.url)
        is_empty = True
    print(database_exists(engine.url))

    import __all_models

    Base.metadata.create_all(engine)

    return is_empty
