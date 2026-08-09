"""Проверки переходов и эскалаций переговорной стейт-машины."""

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.api.routes.negotiation import (
    SCRIPT_TEMPLATES,
    create_draft,
    get_negotiation,
    send_message,
)
from app.models import Chat, Listing, NegotiationStage, User
from app.schemas import NegotiationDraftRequest, NegotiationMessageCreate
from app.services.negotiation import (
    ALLOWED_TRANSITIONS,
    InvalidTransition,
    NegotiationMode,
    process_event,
    transition,
)


@pytest.fixture
def session() -> Session:
    """Создаёт изолированную SQLite-базу для проверок маршрутов."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as database_session:
        yield database_session


def create_listing(session: Session, stage: NegotiationStage) -> Listing:
    """Создаёт минимальный участок в нужной стадии переговоров."""
    listing = Listing(
        title="Участок 10 сот., Домодедово",
        area_sotka=10,
        price_rub=2_100_000,
        negotiation_stage=stage,
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


def fake_user() -> User:
    """Пользователь для прямых вызовов маршрутов в обход HTTP-слоя FastAPI."""
    return User(
        id=1,
        email="manager@test.local",
        full_name="Тестовый менеджер",
        password_hash="x",
    )


def test_happy_path_to_offer() -> None:
    """Обычный сценарий последовательно приводит к подготовке оффера."""
    first = process_event(NegotiationStage.NEW, "start", mode=NegotiationMode.DRAFT)
    assert first.stage == NegotiationStage.NEED_FIRST_CONTACT
    sent = process_event(first.stage, "send_first_message")
    assert sent.stage == NegotiationStage.WAITING_REPLY
    qualified = process_event(
        sent.stage, "incoming_message", message_text="Участок ещё продаётся"
    )
    assert qualified.stage == NegotiationStage.QUALIFIED
    bargain = process_event(qualified.stage, "start_bargain")
    offer = process_event(bargain.stage, "prepare_offer")
    assert offer.stage == NegotiationStage.OFFER_READY


def test_cadastral_number_escalates_to_manager() -> None:
    """Кадастровая тема должна сразу переводить диалог на ручную проверку."""
    result = process_event(
        NegotiationStage.WAITING_REPLY,
        "incoming_message",
        message_text="Кадастровый номер вышлю вечером",
    )
    assert result.stage == NegotiationStage.HUMAN_REVIEW
    assert result.escalated is True
    assert "Обсуждается кадастровый номер" in result.escalation_reasons


def test_discount_above_seven_percent_escalates() -> None:
    """Торг больше 7% не остаётся на автоматическом контуре."""
    result = process_event(
        NegotiationStage.WAITING_REPLY,
        "incoming_message",
        message_text="Готов обсудить цену",
        requested_discount_pct=8,
    )
    assert result.escalated is True
    assert "Торг превышает 7%" in result.escalation_reasons


def test_invalid_transition_is_rejected() -> None:
    """Нельзя перепрыгнуть из нового состояния сразу в оффер."""
    with pytest.raises(InvalidTransition):
        transition(NegotiationStage.NEW, NegotiationStage.OFFER_READY)


@pytest.mark.asyncio
async def test_draft_without_hermes_returns_local_template(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Без Hermes маршрут возвращает детерминированный сценарий, а не ошибку."""
    from app.core.config import settings

    listing = create_listing(session, NegotiationStage.NEED_FIRST_CONTACT)
    monkeypatch.setattr(settings, "hermes_api_url", "")
    result = await create_draft(
        listing.id,
        session,
        fake_user(),
        NegotiationDraftRequest(intent="facts"),
    )
    assert result.draft_message == SCRIPT_TEMPLATES["facts"]
    assert "Домодедово" in result.prompt_used


def test_allowed_actions_match_state_machine(session: Session) -> None:
    """В ответе диалога доступны ровно переходы из общей стейт-машины."""
    listing = create_listing(session, NegotiationStage.QUALIFIED)
    result = get_negotiation(listing.id, session, fake_user())
    assert (
        set(result.allowed_next_actions)
        == ALLOWED_TRANSITIONS[listing.negotiation_stage]
    )


def test_outgoing_message_creates_chat(session: Session) -> None:
    """Первое исходящее сообщение создаёт локальный чат и обновляет его время."""
    listing = create_listing(session, NegotiationStage.NEED_FIRST_CONTACT)
    message = send_message(
        listing.id,
        NegotiationMessageCreate(body="Подскажите, участок ещё продаётся?"),
        session,
        fake_user(),
    )
    chat = session.exec(select(Chat).where(Chat.listing_id == listing.id)).one()
    assert message.direction == "out"
    assert message.sent_by_human is True
    assert chat.last_message_at == message.sent_at
