"""Входящие вебхуки Авито с безопасным журналированием."""

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
