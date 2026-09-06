"""Подключение SQLModel к базе данных."""

from collections.abc import Generator
import sqlite3
from sqlalchemy import event
from sqlalchemy.engine import Engine

from sqlmodel import Session, create_engine

from app.core.config import settings

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)


@event.listens_for(Engine, "connect")
def sqlite_unicode_lower(connection, record):
    # SQLite's built-in lower only handles ASCII; local Russian searches must work too.
    if isinstance(connection, sqlite3.Connection):
        connection.create_function(
            "lower",
            1,
            lambda value: value.casefold() if value is not None else None,
            deterministic=True,
        )


engine = create_engine(
    settings.database_url, echo=False, pool_pre_ping=True, connect_args=connect_args
)


def get_session() -> Generator[Session, None, None]:
    """Выдаёт сессию БД на время обработки HTTP-запроса."""
    with Session(engine) as session:
        yield session
