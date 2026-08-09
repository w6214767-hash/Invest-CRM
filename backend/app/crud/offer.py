"""CRUD-операции для предложений."""

from app.crud.base import CRUDBase
from app.models import Offer
from app.schemas import OfferCreate, OfferUpdate

offer = CRUDBase[Offer, OfferCreate, OfferUpdate](Offer)
