"""CRUD-операции для сделок."""

from app.crud.base import CRUDBase
from app.models import Deal
from app.schemas import DealCreate, DealUpdate

deal = CRUDBase[Deal, DealCreate, DealUpdate](Deal)
