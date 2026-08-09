"""Маршруты работы с объявлениями земельных участков."""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.crud import listing as crud_listing
from app.models import ListingStatus
from app.schemas import ListingCreate, ListingRead, ListingUpdate
from app.services.scoring import detect_red_flags, detect_urgency

router = APIRouter(prefix="/listings", tags=["Объявления"])


@router.get("", response_model=list[ListingRead])
def list_listings(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
):
    """Возвращает ранжированный список объявлений."""
    return crud_listing.get_ranked(session, limit=limit)[skip:]


@router.post("", response_model=ListingRead, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreate, session: SessionDep, current_user: CurrentUser
):
    """Создаёт объявление и заполняет производные поля первичного скоринга."""
    data = payload.model_dump()
    data["price_per_sotka"] = round(payload.price_rub / payload.area_sotka, 2)
    urgency, _ = detect_urgency(payload.description)
    data["seller_urgency_score"] = urgency
    data["red_flags"] = detect_red_flags(payload.description, payload.cadastral_number)
    data["status"] = ListingStatus.NEW
    return crud_listing.create(session, obj_in=data)


@router.get("/{listing_id}", response_model=ListingRead)
def get_listing(listing_id: int, session: SessionDep, current_user: CurrentUser):
    """Возвращает одно объявление."""
    item = crud_listing.get(session, listing_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return item


@router.patch("/{listing_id}", response_model=ListingRead)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Обновляет карточку объявления."""
    item = crud_listing.get(session, listing_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    updated = crud_listing.update(session, db_obj=item, obj_in=payload)
    if payload.price_rub is not None or payload.area_sotka is not None:
        updated.price_per_sotka = round(updated.price_rub / updated.area_sotka, 2)
        session.add(updated)
        session.commit()
        session.refresh(updated)
    return updated


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int, session: SessionDep, current_user: CurrentUser
) -> None:
    """Удаляет объявление из локальной CRM."""
    if crud_listing.remove(session, entity_id=listing_id) is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
