"""Проверки переходов и эскалаций переговорной стейт-машины."""

import pytest

from app.models import NegotiationStage
from app.services.negotiation import (
    InvalidTransition,
    NegotiationMode,
    process_event,
    transition,
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
