"""Клиент REST Bitrix24 через входящий вебхук."""

from typing import Any

import httpx

from app.core.config import settings


class Bitrix24Client:
    """Создаёт лиды, сделки и комментарии в подключённом Bitrix24."""

    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = (webhook_url or settings.bitrix24_webhook_url).rstrip("/")

    async def call(self, method: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Вызывает метод REST API и проверяет бизнес-ошибку Bitrix24."""
        if not self.webhook_url:
            raise RuntimeError("Не задан BITRIX24_WEBHOOK_URL")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.webhook_url}/{method}.json", json={"fields": fields}
            )
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(f"Bitrix24: {payload['error_description']}")
        return payload

    async def add_lead(self, fields: dict[str, Any]) -> int:
        """Создаёт лид CRM и возвращает его идентификатор."""
        return int((await self.call("crm.lead.add", fields))["result"])

    async def add_deal(self, fields: dict[str, Any]) -> int:
        """Создаёт сделку CRM и возвращает её идентификатор."""
        return int((await self.call("crm.deal.add", fields))["result"])

    async def add_timeline_comment(self, entity_id: int, comment: str) -> int:
        """Добавляет комментарий в таймлайн сделки."""
        payload = await self.call(
            "crm.timeline.comment.add",
            {"ENTITY_ID": entity_id, "ENTITY_TYPE": "deal", "COMMENT": comment},
        )
        return int(payload["result"])
