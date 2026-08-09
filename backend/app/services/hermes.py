"""Адаптер Hermes Agent для подсказок менеджеру по переговорам."""

from typing import Any

import httpx

from app.core.config import settings

FIRST_MESSAGE_PROMPT = """Ты помощник менеджера ЮрЖилСервис. Составь вежливое короткое первое сообщение продавцу земельного участка. Не обещай покупку, не дави, задай до двух нейтральных уточняющих вопросов о документах и доступности просмотра. Объявление: {listing}."""
CLASSIFY_REPLY_PROMPT = """Классифицируй ответ продавца земельного участка для CRM. Верни JSON с ключами intent, sentiment, has_cadastral_number, asks_discount_pct, ready_for_advance, legal_risk. Ответ: {reply}"""
DIALOG_SUMMARY_PROMPT = """Сделай лаконичное резюме диалога по земельному участку: цена, готовность к торгу, документы, риски, следующий шаг. Диалог: {dialog}"""


class HermesClient:
    """Вызывает совместимый HTTP-интерфейс Hermes Agent."""

    async def complete(self, prompt: str) -> str:
        """Передаёт промпт Hermes и извлекает текст из типовых форматов ответа."""
        if not settings.hermes_api_url:
            raise RuntimeError("Не задан HERMES_API_URL")
        headers = (
            {"Authorization": f"Bearer {settings.hermes_api_key}"}
            if settings.hermes_api_key
            else {}
        )
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                settings.hermes_api_url, json={"prompt": prompt}, headers=headers
            )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        for key in ("text", "response", "content"):
            if isinstance(payload.get(key), str):
                return payload[key]
        raise RuntimeError("Hermes вернул ответ без текстового поля")

    async def generate_first_message(self, listing: str) -> str:
        """Генерирует черновик первого обращения."""
        return await self.complete(FIRST_MESSAGE_PROMPT.format(listing=listing))

    async def classify_seller_reply(self, reply: str) -> str:
        """Классифицирует реплику продавца для правил переговоров."""
        return await self.complete(CLASSIFY_REPLY_PROMPT.format(reply=reply))

    async def summarize_dialog(self, dialog: str) -> str:
        """Составляет резюме диалога для карточки лота."""
        return await self.complete(DIALOG_SUMMARY_PROMPT.format(dialog=dialog))
