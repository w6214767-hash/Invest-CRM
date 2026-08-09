"""Тесты постоянного профиля поиска и журнала автоматизации."""

from sqlmodel import Session, SQLModel, create_engine

from app.api.routes.integrations import overview, run_search, update_profile
from app.schemas.integrations import SearchProfilePayload


def session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_profile_is_created_and_updated() -> None:
    with session() as db:
        initial = overview(db)
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
        )
        assert updated.name == "Новый профиль"
        assert updated.districts == ["Чехов"]


def test_run_is_written_to_audit() -> None:
    with session() as db:
        result = run_search(db)
        assert result.run_id > 0
        data = overview(db)
        assert data.metrics["runs"] == 1
        assert data.audit[0].action == "Профиль поиска обработан"
