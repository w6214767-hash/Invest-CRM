"""Маршруты диалогов и стейт-машины переговоров."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import SessionDep
from app.core.config import settings
from app.models import (
    Chat,
    Listing,
    Message,
    NegotiationEvent,
    NegotiationStage,
    Seller,
)
from app.schemas import (
    NegotiationAction,
    NegotiationDetail,
    NegotiationDraftRequest,
    NegotiationDraftResponse,
    NegotiationEventRead,
    NegotiationListItem,
    NegotiationListingSummary,
    NegotiationMessageCreate,
    NegotiationMessagePreview,
    NegotiationMessageRead,
    NegotiationResult,
    NegotiationSellerSummary,
)
from app.services.hermes import HermesClient
from app.services.negotiation import (
    ALLOWED_TRANSITIONS,
    InvalidTransition,
    NegotiationMode,
    process_event,
)

router = APIRouter(prefix="/negotiation", tags=["Переговоры"])

SCRIPT_TEMPLATES = {
    "first_contact": (
        "Здравствуйте! Подскажите, пожалуйста, участок ещё актуален? "
        "Если да, удобно ли сегодня коротко уточнить детали и договориться о просмотре?"
    ),
    "facts": (
        "Спасибо. Чтобы подготовиться к просмотру, уточните, пожалуйста: "
        "как оформлены коммуникации, какой подъезд к участку зимой, есть ли "
        "обременения и завершено ли межевание?"
    ),
    "motivation": (
        "Подскажите, пожалуйста, насколько срочна продажа и что для вас важно "
        "по срокам выхода на сделку? Рассматриваете быстрый задаток при понятных условиях?"
    ),
    "bargain_test": (
        "Если по документам всё в порядке и мы сможем быстро согласовать задаток, "
        "готовы ли вы обсудить цену? Какой минимум для вас был бы предметом разговора?"
    ),
}

PROMPT_TEMPLATES = {
    "first_contact": (
        "Составь вежливое короткое первое сообщение продавцу участка. Проверь "
        "актуальность и предложи согласовать просмотр. Не обещай покупку. Лот: {listing}."
    ),
    "facts": (
        "Составь короткое вежливое сообщение продавцу участка: уточни коммуникации, "
        "подъезд, обременения и межевание. Не обещай покупку. Лот: {listing}."
    ),
    "motivation": (
        "Составь нейтральное сообщение продавцу участка: выясни срочность продажи, "
        "важные для него сроки и готовность к быстрому задатку. Не дави. Лот: {listing}."
    ),
    "bargain_test": (
        "Составь деликатное сообщение продавцу участка: проверь готовность обсуждать "
        "торг при быстром задатке и чистых документах. Не называй цену и не дави. Лот: {listing}."
    ),
}


def _get_listing_or_404(session: Session, listing_id: int) -> Listing:
    """Возвращает участок либо единообразную ошибку отсутствия."""
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return listing


def _get_seller(session: Session, listing: Listing) -> Seller | None:
    """Загружает продавца, если он привязан к участку."""
    if listing.seller_id is None:
        return None
    return session.get(Seller, listing.seller_id)


def _get_chat(session: Session, listing_id: int) -> Chat | None:
    """Возвращает последний активный чат участка."""
    return session.exec(
        select(Chat)
        .where(Chat.listing_id == listing_id)
        .order_by(Chat.last_message_at.desc(), Chat.id.desc())
    ).first()


def _get_messages(session: Session, chat: Chat | None) -> list[Message]:
    """Возвращает сообщения чата в естественном порядке."""
    if chat is None or chat.id is None:
        return []
    return list(
        session.exec(
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(Message.sent_at, Message.id)
        ).all()
    )


def _get_events(session: Session, listing_id: int) -> list[NegotiationEvent]:
    """Возвращает историю переходов переговоров от старых к новым."""
    return list(
        session.exec(
            select(NegotiationEvent)
            .where(NegotiationEvent.listing_id == listing_id)
            .order_by(NegotiationEvent.created_at, NegotiationEvent.id)
        ).all()
    )


def _event_escalation_reasons(event: NegotiationEvent) -> list[str]:
    """Извлекает из JSON-аудита только текстовые причины эскалации."""
    reasons = event.metadata_json.get("escalation_reasons", [])
    if not isinstance(reasons, list):
        return []
    return [reason for reason in reasons if isinstance(reason, str)]


def _all_escalation_reasons(events: list[NegotiationEvent]) -> list[str]:
    """Собирает уникальные причины эскалации с сохранением их порядка."""
    reasons: list[str] = []
    for event in events:
        for reason in _event_escalation_reasons(event):
            if reason not in reasons:
                reasons.append(reason)
    return reasons


def _draft_prompt(intent: str, listing: Listing) -> str:
    """Формирует инструкцию Hermes с контекстом конкретного участка."""
    district = listing.district or listing.region or "район не указан"
    listing_context = (
        f"{listing.title}; район: {district}; цена: {listing.price_rub} ₽; "
        f"стадия: {listing.negotiation_stage.value}."
    )
    return PROMPT_TEMPLATES[intent].format(listing=listing_context)


@router.get("", response_model=list[NegotiationListItem])
def list_negotiations(session: SessionDep) -> list[NegotiationListItem]:
    """Возвращает активные переговоры, отсортированные по последнему сообщению."""
    listings = list(
        session.exec(
            select(Listing).where(
                Listing.negotiation_stage != NegotiationStage.ARCHIVED
            )
        ).all()
    )
    result: list[NegotiationListItem] = []
    for listing in listings:
        chat = _get_chat(session, listing.id)
        messages = _get_messages(session, chat)
        events = _get_events(session, listing.id)
        seller = _get_seller(session, listing)
        last_message = messages[-1] if messages else None
        unread_count = sum(
            1
            for message in messages
            if message.direction == "in" and not message.is_read
        )
        escalation_reasons = _all_escalation_reasons(events)
        result.append(
            NegotiationListItem(
                listing_id=listing.id,
                title=listing.title,
                district=listing.district or listing.region,
                price_rub=listing.price_rub,
                discount_pct=listing.discount_pct,
                score=listing.score,
                stage=listing.negotiation_stage,
                seller_name=seller.name if seller else None,
                last_message=(
                    NegotiationMessagePreview(
                        body=last_message.body, sent_at=last_message.sent_at
                    )
                    if last_message
                    else None
                ),
                unread_count=unread_count,
                escalated=bool(escalation_reasons)
                or listing.negotiation_stage == NegotiationStage.HUMAN_REVIEW,
            )
        )
    return sorted(
        result,
        key=lambda item: item.last_message.sent_at
        if item.last_message
        else datetime.min,
        reverse=True,
    )


@router.get("/{listing_id}", response_model=NegotiationDetail)
def get_negotiation(listing_id: int, session: SessionDep) -> NegotiationDetail:
    """Возвращает полный диалог, аудит и допустимые переходы участка."""
    listing = _get_listing_or_404(session, listing_id)
    seller = _get_seller(session, listing)
    chat = _get_chat(session, listing_id)
    messages = _get_messages(session, chat)
    events = _get_events(session, listing_id)
    escalation_reasons = _all_escalation_reasons(events)
    return NegotiationDetail(
        listing=NegotiationListingSummary(
            id=listing.id,
            title=listing.title,
            district=listing.district or listing.region,
            price_rub=listing.price_rub,
            discount_pct=listing.discount_pct,
            score=listing.score,
        ),
        seller=NegotiationSellerSummary(
            name=seller.name if seller else None,
            seller_type=seller.seller_type if seller else "unknown",
            urgency_score=(
                seller.urgency_score if seller else listing.seller_urgency_score
            ),
        ),
        messages=[
            NegotiationMessageRead(
                id=message.id,
                direction=message.direction,
                body=message.body,
                sent_at=message.sent_at,
                sent_by_human=message.sent_by_human,
            )
            for message in messages
        ],
        events=[
            NegotiationEventRead(
                id=event.id,
                from_stage=event.from_stage,
                to_stage=event.to_stage,
                reason=event.reason,
                actor=event.actor,
                escalation_reasons=_event_escalation_reasons(event),
                created_at=event.created_at,
            )
            for event in events
        ],
        stage=listing.negotiation_stage,
        allowed_next_actions=sorted(
            ALLOWED_TRANSITIONS[listing.negotiation_stage],
            key=lambda stage: stage.value,
        ),
        escalated=bool(escalation_reasons)
        or listing.negotiation_stage == NegotiationStage.HUMAN_REVIEW,
        escalation_reasons=escalation_reasons,
    )


@router.post("/{listing_id}/draft", response_model=NegotiationDraftResponse)
async def create_draft(
    listing_id: int,
    session: SessionDep,
    payload: NegotiationDraftRequest | None = None,
) -> NegotiationDraftResponse:
    """Генерирует черновик Hermes либо использует безопасный локальный шаблон."""
    listing = _get_listing_or_404(session, listing_id)
    intent = payload.intent if payload and payload.intent else "first_contact"
    prompt = _draft_prompt(intent, listing)
    if not settings.hermes_api_url:
        return NegotiationDraftResponse(
            draft_message=SCRIPT_TEMPLATES[intent], prompt_used=prompt
        )
    draft = await HermesClient().complete(prompt)
    return NegotiationDraftResponse(draft_message=draft, prompt_used=prompt)


@router.post(
    "/{listing_id}/message",
    response_model=NegotiationMessageRead,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    listing_id: int, payload: NegotiationMessageCreate, session: SessionDep
) -> NegotiationMessageRead:
    """Сохраняет исходящее сообщение менеджера и при необходимости создаёт чат."""
    listing = _get_listing_or_404(session, listing_id)
    chat = _get_chat(session, listing_id)
    if chat is None:
        chat = Chat(
            avito_chat_id=f"local-listing-{listing.id}",
            listing_id=listing.id,
            seller_id=listing.seller_id,
        )
        session.add(chat)
        session.flush()
    message = Message(
        chat_id=chat.id,
        direction="out",
        body=payload.body.strip(),
        sent_by_human=True,
        is_read=True,
    )
    chat.last_message_at = message.sent_at
    session.add(message)
    session.add(chat)
    session.commit()
    session.refresh(message)
    return NegotiationMessageRead(
        id=message.id,
        direction=message.direction,
        body=message.body,
        sent_at=message.sent_at,
        sent_by_human=message.sent_by_human,
    )


@router.post("/{listing_id}/action", response_model=NegotiationResult)
def negotiation_action(
    listing_id: int, payload: NegotiationAction, session: SessionDep
) -> NegotiationResult:
    """Применяет событие к переговорам и записывает его в аудит."""
    listing = _get_listing_or_404(session, listing_id)
    try:
        mode = NegotiationMode(payload.mode)
        decision = process_event(
            listing.negotiation_stage,
            payload.action,
            message_text=payload.message_text,
            mode=mode,
        )
    except (ValueError, InvalidTransition) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    event = NegotiationEvent(
        listing_id=listing.id,
        from_stage=listing.negotiation_stage,
        to_stage=decision.stage,
        reason=payload.action,
        actor=payload.actor,
        metadata_json={
            "mode": mode.value,
            "escalation_reasons": decision.escalation_reasons,
        },
    )
    listing.negotiation_stage = decision.stage
    session.add(listing)
    session.add(event)
    session.commit()
    return NegotiationResult(
        stage=decision.stage,
        escalated=decision.escalated,
        escalation_reasons=decision.escalation_reasons,
        draft_message=decision.draft_message,
    )
