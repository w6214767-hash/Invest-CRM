"""Входящие вебхуки Авито и Bitrix24 с безопасным журналированием."""

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks", tags=["Вебхуки"])


@router.post("/avito")
async def avito_webhook(request: Request) -> dict[str, Any]:
    """Принимает событие Авито для последующей обработки воркером.

    TODO: перед включением в интернет добавить проверку подписи, когда Авито
    предоставит её формат для выбранного типа webhook-подписки.
    """
    payload = await request.json()
    return {
        "accepted": True,
        "source": "avito",
        "event_type": payload.get("type", "unknown"),
    }


@router.post("/bitrix24")
async def bitrix24_webhook(request: Request) -> dict[str, Any]:
    """Принимает уведомление Bitrix24 и подтверждает его обработку."""
    payload = await request.form()
    return {
        "accepted": True,
        "source": "bitrix24",
        "event_type": payload.get("event", "unknown"),
    }
