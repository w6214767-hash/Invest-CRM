"""Маршруты карточек продавцов."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.crud import seller as crud_seller
from app.schemas import SellerCreate, SellerRead, SellerUpdate

router = APIRouter(prefix="/sellers", tags=["Продавцы"])


@router.get("", response_model=list[SellerRead])
def list_sellers(session: SessionDep, current_user: CurrentUser):
    """Возвращает продавцов."""
    return crud_seller.get_multi(session)


@router.post("", response_model=SellerRead, status_code=status.HTTP_201_CREATED)
def create_seller(
    payload: SellerCreate, session: SessionDep, current_user: CurrentUser
):
    """Создаёт карточку продавца."""
    return crud_seller.create(session, obj_in=payload)


@router.get("/{seller_id}", response_model=SellerRead)
def get_seller(seller_id: int, session: SessionDep, current_user: CurrentUser):
    """Возвращает продавца по идентификатору."""
    result = crud_seller.get(session, seller_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Продавец не найден")
    return result


@router.patch("/{seller_id}", response_model=SellerRead)
def update_seller(
    seller_id: int,
    payload: SellerUpdate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Изменяет карточку продавца."""
    result = crud_seller.get(session, seller_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Продавец не найден")
    return crud_seller.update(session, db_obj=result, obj_in=payload)
