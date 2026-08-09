"""Маршруты инвестиционных сделок."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.crud import deal as crud_deal
from app.schemas import DealCreate, DealRead, DealUpdate

router = APIRouter(prefix="/deals", tags=["Сделки"])


@router.get("", response_model=list[DealRead])
def list_deals(session: SessionDep, current_user: CurrentUser):
    """Возвращает сделки."""
    return crud_deal.get_multi(session)


@router.post("", response_model=DealRead, status_code=status.HTTP_201_CREATED)
def create_deal(payload: DealCreate, session: SessionDep, current_user: CurrentUser):
    """Создаёт локальную сделку для дальнейшей передачи в Bitrix24."""
    return crud_deal.create(session, obj_in=payload)


@router.get("/{deal_id}", response_model=DealRead)
def get_deal(deal_id: int, session: SessionDep, current_user: CurrentUser):
    """Возвращает сделку."""
    result = crud_deal.get(session, deal_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    return result


@router.patch("/{deal_id}", response_model=DealRead)
def update_deal(
    deal_id: int, payload: DealUpdate, session: SessionDep, current_user: CurrentUser
):
    """Обновляет стадию и реквизиты сделки."""
    result = crud_deal.get(session, deal_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    return crud_deal.update(session, db_obj=result, obj_in=payload)
