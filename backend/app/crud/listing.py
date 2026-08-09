"""CRUD-операции для объявлений."""

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Listing
from app.schemas import ListingCreate, ListingUpdate


class CRUDListing(CRUDBase[Listing, ListingCreate, ListingUpdate]):
    """Специализированная выборка объявлений."""

    def get_ranked(self, session: Session, *, limit: int = 100) -> list[Listing]:
        """Возвращает объявления в порядке инвестиционного балла."""
        statement = select(Listing).order_by(Listing.score.desc()).limit(limit)
        return list(session.exec(statement).all())


listing = CRUDListing(Listing)
