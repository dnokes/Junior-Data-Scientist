from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlmodel import Session, SQLModel, create_engine

from carms.core.config import Settings

settings = Settings()
engine = create_engine(settings.db_url, echo=False)


def get_engine():
    return engine


@asynccontextmanager
async def session_scope() -> AsyncIterator[Session]:
    """Async-friendly context manager for explicit transactional scopes."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_session() -> AsyncIterator[Session]:
    """FastAPI dependency that yields a database session."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Import models and create tables if they do not exist."""
    import carms.models.bronze  # noqa: F401
    import carms.models.silver  # noqa: F401
    import carms.models.gold  # noqa: F401

    SQLModel.metadata.create_all(engine)
