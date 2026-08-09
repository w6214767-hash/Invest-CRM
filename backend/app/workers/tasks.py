"""Асинхронные задания, совместимые с вызовом из ARQ либо Celery-обёртки."""

from sqlmodel import Session, select

from app.core.db import engine
from app.models import Listing
from app.services.avito import AvitoClient
from app.services.scoring import evaluate_listing
from app.services.telegram import TelegramNotifier


async def sync_avito_listings(
    _: object | None = None, *, user_id: int | None = None
) -> dict:
    """Получает объявления Авито; маппинг конкретного payload добавляется в адаптере аккаунта."""
    if user_id is None:
        return {"status": "skipped", "reason": "Не задан идентификатор аккаунта Авито"}
    payload = await AvitoClient().get_listings(user_id)
    return {
        "status": "received",
        "items": len(payload.get("resources", payload.get("items", []))),
    }


async def rescore_listings(_: object | None = None) -> dict:
    """Пересчитывает локальный скоринг с собственной ценой как временной базой."""
    changed = 0
    with Session(engine) as session:
        listings = list(session.exec(select(Listing)).all())
        for item in listings:
            result = evaluate_listing(
                price_rub=item.price_rub,
                area_sotka=item.area_sotka,
                cluster_prices_per_sotka=[
                    item.price_per_sotka or item.price_rub / item.area_sotka
                ],
                description=item.description,
                liquidity=item.liquidity_score,
                location=item.location_score,
                docs=item.docs_score,
                utility=item.utility_score,
                cadastral_number=item.cadastral_number,
            )
            item.price_per_sotka = round(item.price_rub / item.area_sotka, 2)
            item.discount_pct = result.discount_pct
            item.score = result.score
            item.seller_urgency_score = result.urgency_score
            item.red_flags = result.red_flags
            session.add(item)
            changed += 1
        session.commit()
    return {"status": "ok", "rescored": changed}


async def poll_chats(_: object | None = None, *, user_id: int | None = None) -> dict:
    """Запрашивает список чатов для интеграционной очереди."""
    if user_id is None:
        return {"status": "skipped", "reason": "Не задан идентификатор аккаунта Авито"}
    payload = await AvitoClient().get_chats(user_id)
    return {"status": "received", "chats": len(payload.get("chats", []))}


async def daily_digest(_: object | None = None) -> dict:
    """Отправляет менеджеру количество лотов, требующих внимания."""
    with Session(engine) as session:
        listings = list(session.exec(select(Listing)).all())
    urgent = [item for item in listings if item.score is not None and item.score >= 65]
    lines = [
        f"Новых/оценённых лотов: {len(listings)}",
        f"Приоритетных лотов (балл ≥ 65): {len(urgent)}",
    ]
    result = await TelegramNotifier().send_digest(lines)
    return {"status": "sent", "message_id": result.get("message_id")}
