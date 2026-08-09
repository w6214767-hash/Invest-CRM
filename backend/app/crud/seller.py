"""CRUD-операции для продавцов."""

from app.crud.base import CRUDBase
from app.models import Seller
from app.schemas import SellerCreate, SellerUpdate

seller = CRUDBase[Seller, SellerCreate, SellerUpdate](Seller)
