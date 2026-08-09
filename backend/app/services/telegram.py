"""Уведомления и ежедневные дайджесты в Telegram."""

import httpx

from app.core.config import settings


class TelegramNotifier:
    """Минимальный клиент Telegram Bot API."""

    async def send_message(self, text: str, *, chat_id: str | None = None) -> dict:
        """Отправляет сообщение в настроенный чат."""
        token = settings.telegram_bot_token
        destination = chat_id or settings.telegram_chat_id
        if not token or not destination:
            raise RuntimeError("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": destination, "text": text, "parse_mode": "HTML"},
            )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram отклонил сообщение: {payload}")
        return payload["result"]

    async def send_digest(self, lines: list[str]) -> dict:
        """Формирует и отправляет компактный дневной дайджест."""
        body = "<b>ЮрЖил CRM — дневной дайджест</b>\n\n" + "\n".join(lines)
        return await self.send_message(body)
