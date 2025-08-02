from contextlib import contextmanager

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from xarizmi.config import get_config


@contextmanager
def session_scope():  # type: ignore
    """Provide a transactional scope around a series of operations."""
    session = get_config().session_maker()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def get_engine() -> Engine:
    return get_config().db_engine
