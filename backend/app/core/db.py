"""Подключение SQLModel к базе данных."""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(
    settings.database_url, echo=False, pool_pre_ping=True, connect_args=connect_args
)


def get_session() -> Generator[Session, None, None]:
    """Выдаёт сессию БД на время обработки HTTP-запроса."""
    with Session(engine) as session:
        yield session
