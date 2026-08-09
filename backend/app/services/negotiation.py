"""Детерминированная стейт-машина полуавтоматических переговоров."""

from dataclasses import dataclass
from enum import Enum

from app.models import NegotiationStage


class NegotiationMode(str, Enum):
    """Степень автономности помощника в переписке."""

    DRAFT = "draft"
    ASSISTED = "assisted"
    NEGOTIATION = "negotiation"


class InvalidTransition(ValueError):
    """Сигнализирует о недопустимом переходе между стадиями."""


@dataclass(frozen=True)
class NegotiationDecision:
    """Решение стейт-машины с информацией для интерфейса и аудита."""

    stage: NegotiationStage
    escalated: bool
    escalation_reasons: list[str]
    draft_message: str | None = None


ALLOWED_TRANSITIONS: dict[NegotiationStage, set[NegotiationStage]] = {
    NegotiationStage.NEW: {
        NegotiationStage.NEED_FIRST_CONTACT,
        NegotiationStage.ARCHIVED,
    },
    NegotiationStage.NEED_FIRST_CONTACT: {
        NegotiationStage.WAITING_REPLY,
        NegotiationStage.ARCHIVED,
    },
    NegotiationStage.WAITING_REPLY: {
        NegotiationStage.QUALIFIED,
        NegotiationStage.HUMAN_REVIEW,
        NegotiationStage.ARCHIVED,
    },
    NegotiationStage.QUALIFIED: {
        NegotiationStage.BARGAIN_STARTED,
        NegotiationStage.OFFER_READY,
        NegotiationStage.HUMAN_REVIEW,
        NegotiationStage.ARCHIVED,
    },
    NegotiationStage.BARGAIN_STARTED: {
        NegotiationStage.OFFER_READY,
        NegotiationStage.HUMAN_REVIEW,
        NegotiationStage.ARCHIVED,
    },
    NegotiationStage.HUMAN_REVIEW: {
        NegotiationStage.QUALIFIED,
        NegotiationStage.BARGAIN_STARTED,
        NegotiationStage.OFFER_READY,
        NegotiationStage.ARCHIVED,
    },
    NegotiationStage.OFFER_READY: {NegotiationStage.ARCHIVED},
    NegotiationStage.ARCHIVED: set(),
}


def transition(current: NegotiationStage, target: NegotiationStage) -> NegotiationStage:
    """Проверяет и возвращает разрешённый переход состояния."""
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransition(f"Переход {current.value} → {target.value} не разрешён")
    return target


def detect_escalation_reasons(
    text: str, *, requested_discount_pct: float | None = None
) -> list[str]:
    """Выявляет обязательные условия передачи диалога живому менеджеру."""
    normalized = text.casefold()
    reasons: list[str] = []
    if "кадастров" in normalized or "кад. номер" in normalized:
        reasons.append("Обсуждается кадастровый номер")
    if requested_discount_pct is not None and requested_discount_pct > 7:
        reasons.append("Торг превышает 7%")
    if any(token in normalized for token in ("аванс", "задаток", "предоплат")):
        reasons.append("Продавец готов обсуждать аванс")
    if any(
        token in normalized
        for token in ("обремен", "арест", "суд", "доля", "наследств")
    ):
        reasons.append("Обнаружен юридический риск")
    if any(
        token in normalized for token in ("не пишите", "надоели", "достали", "жалоб")
    ):
        reasons.append("Продавец раздражён")
    return reasons


def process_event(
    current: NegotiationStage,
    action: str,
    *,
    message_text: str = "",
    requested_discount_pct: float | None = None,
    mode: NegotiationMode = NegotiationMode.ASSISTED,
) -> NegotiationDecision:
    """Обрабатывает бизнес-событие и возвращает следующую стадию.

    Режимы draft и assisted не отправляют сообщения сами: функция создаёт лишь
    черновик. Режим negotiation также требует отдельного явного вызова клиента Авито,
    что сохраняет контроль над отправкой в воркере.
    """
    if action == "start":
        target = transition(current, NegotiationStage.NEED_FIRST_CONTACT)
        return NegotiationDecision(
            target, False, [], "Здравствуйте! Подскажите, участок ещё продаётся?"
        )
    if action == "send_first_message":
        target = transition(current, NegotiationStage.WAITING_REPLY)
        draft = message_text or "Здравствуйте! Подскажите, участок ещё продаётся?"
        return NegotiationDecision(target, False, [], draft)
    if action == "incoming_message":
        reasons = detect_escalation_reasons(
            message_text, requested_discount_pct=requested_discount_pct
        )
        if reasons:
            target = transition(current, NegotiationStage.HUMAN_REVIEW)
            return NegotiationDecision(target, True, reasons)
        target = transition(current, NegotiationStage.QUALIFIED)
        return NegotiationDecision(target, False, [])
    if action == "start_bargain":
        return NegotiationDecision(
            transition(current, NegotiationStage.BARGAIN_STARTED), False, []
        )
    if action == "prepare_offer":
        return NegotiationDecision(
            transition(current, NegotiationStage.OFFER_READY), False, []
        )
    if action == "archive":
        return NegotiationDecision(
            transition(current, NegotiationStage.ARCHIVED), False, []
        )
    if action == "manager_resume":
        return NegotiationDecision(
            transition(current, NegotiationStage.QUALIFIED), False, []
        )
    if action == "manager_escalate":
        return NegotiationDecision(
            transition(current, NegotiationStage.HUMAN_REVIEW),
            True,
            ["Ручная эскалация менеджера"],
        )
    raise ValueError(f"Неизвестное действие переговоров: {action}; режим: {mode.value}")
