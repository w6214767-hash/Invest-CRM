"""Маршруты управления стейт-машиной переговоров."""

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models import NegotiationEvent
from app.schemas import NegotiationAction, NegotiationResult
from app.services.negotiation import InvalidTransition, NegotiationMode, process_event

router = APIRouter(prefix="/negotiation", tags=["Переговоры"])


@router.post("/{listing_id}/action", response_model=NegotiationResult)
def negotiation_action(
    listing_id: int, payload: NegotiationAction, session: SessionDep
) -> NegotiationResult:
    """Применяет событие к переговорам и записывает его в аудит."""
    from app.models import Listing

    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
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
