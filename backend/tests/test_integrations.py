"""Тесты постоянного профиля поиска и журнала автоматизации."""

from sqlmodel import Session, SQLModel, create_engine

from app.api.routes.integrations import overview, run_search, update_profile
from app.models import User
from app.schemas.integrations import SearchProfilePayload


def session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def fake_user() -> User:
    """Пользователь для прямых вызовов маршрутов в обход HTTP-слоя FastAPI."""
    return User(
        id=1,
        email="manager@test.local",
        full_name="Тестовый менеджер",
        password_hash="x",
    )


def test_profile_is_created_and_updated() -> None:
    with session() as db:
        user = fake_user()
        initial = overview(db, user)
        assert initial.profile.name == "Юг Московской области"
        updated = update_profile(
            SearchProfilePayload(
                name="Новый профиль",
                districts=["Чехов"],
                min_price=1,
                max_price=2,
                min_area=1,
                max_area=2,
                min_discount=10,
                land_use=["ИЖС"],
                exclude_words=[],
            ),
            db,
            user,
        )
        assert updated.name == "Новый профиль"
        assert updated.districts == ["Чехов"]


def test_run_is_written_to_audit() -> None:
    with session() as db:
        user = fake_user()
        result = run_search(db, user)
        assert result.run_id > 0
        data = overview(db, user)
        assert data.metrics["runs"] == 1
        assert data.audit[0].action == "Профиль поиска обработан"
