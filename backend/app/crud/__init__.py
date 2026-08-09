"""Экспорт доступных CRUD-репозиториев."""

from app.crud.deal import deal
from app.crud.listing import listing
from app.crud.offer import offer
from app.crud.seller import seller

__all__ = ["deal", "listing", "offer", "seller"]
