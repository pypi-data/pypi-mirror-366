from sqlmodel import SQLModel

from castlecraft_engineer.database.connection import get_engine
from castlecraft_engineer.database.settings_storage import Singles  # noqa: F401


def bootstrap():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
