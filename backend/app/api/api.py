"""Сборка маршрутов API версии 1."""

from fastapi import APIRouter

from app.api.routes import (
    analytics,
    auth,
    deals,
    listings,
    negotiation,
    offers,
    sellers,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(listings.router)
api_router.include_router(sellers.router)
api_router.include_router(deals.router)
api_router.include_router(offers.router)
api_router.include_router(negotiation.router)
api_router.include_router(webhooks.router)
api_router.include_router(analytics.router)
