"""Дашбордные метрики CRM."""

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Deal, DealStage, Listing
from app.schemas import DashboardMetrics

router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard_metrics(
    session: SessionDep, current_user: CurrentUser
) -> DashboardMetrics:
    """Считает число лидов, конверсию, средний дисконт и активные сделки."""
    listings = list(session.exec(select(Listing)).all())
    deals = list(session.exec(select(Deal)).all())
    won_count = sum(1 for deal in deals if deal.stage == DealStage.WON)
    active_deals = sum(
        1 for deal in deals if deal.stage not in (DealStage.WON, DealStage.LOST)
    )
    discounts = [
        listing.discount_pct for listing in listings if listing.discount_pct is not None
    ]
    return DashboardMetrics(
        leads_count=len(listings),
        conversion_pct=round((won_count / len(deals) * 100) if deals else 0, 2),
        average_discount_pct=round(sum(discounts) / len(discounts), 2)
        if discounts
        else 0,
        active_deals_count=active_deals,
    )
