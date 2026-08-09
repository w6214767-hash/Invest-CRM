"""Маршруты предложений о покупке."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.crud import offer as crud_offer
from app.schemas import OfferCreate, OfferRead, OfferUpdate

router = APIRouter(prefix="/offers", tags=["Предложения"])


@router.get("", response_model=list[OfferRead])
def list_offers(session: SessionDep, current_user: CurrentUser):
    """Возвращает предложения."""
    return crud_offer.get_multi(session)


@router.post("", response_model=OfferRead, status_code=status.HTTP_201_CREATED)
def create_offer(payload: OfferCreate, session: SessionDep, current_user: CurrentUser):
    """Создаёт черновик предложения."""
    return crud_offer.create(session, obj_in=payload)


@router.patch("/{offer_id}", response_model=OfferRead)
def update_offer(
    offer_id: int, payload: OfferUpdate, session: SessionDep, current_user: CurrentUser
):
    """Изменяет сумму, статус или срок предложения."""
    result = crud_offer.get(session, offer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Предложение не найдено")
    return crud_offer.update(session, db_obj=result, obj_in=payload)
