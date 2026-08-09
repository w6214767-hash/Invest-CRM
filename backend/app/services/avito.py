"""Асинхронный клиент Avito Business API с ограничением частоты запросов."""

import asyncio
import time
from typing import Any

import httpx

from app.core.config import settings


class AvitoAPIError(RuntimeError):
    """Ошибка ответа Avito Business API."""


class AvitoClient:
    """Клиент OAuth2 и API объявлений/мессенджера Авито.

    Перед продуктивным включением проверьте права приложения и версии путей в
    кабинете Авито: состав полей и доступность методов зависит от подключённого продукта.
    """

    token_url = "https://api.avito.ru/token"
    api_base_url = "https://api.avito.ru"

    def __init__(self, *, requests_per_second: float = 4.0) -> None:
        self.client_id = settings.avito_client_id
        self.client_secret = settings.avito_client_secret
        self._token: str | None = None
        self._token_expires_at = 0.0
        self._lock = asyncio.Lock()
        self._min_interval = 1 / requests_per_second
        self._last_request_at = 0.0

    async def _rate_limit(self) -> None:
        """Соблюдает консервативный интервал между исходящими запросами."""
        async with self._lock:
            delay = self._min_interval - (time.monotonic() - self._last_request_at)
            if delay > 0:
                await asyncio.sleep(delay)
            self._last_request_at = time.monotonic()

    async def get_access_token(self) -> str:
        """Запрашивает OAuth2 client_credentials токен и кэширует его."""
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        if not self.client_id or not self.client_secret:
            raise AvitoAPIError("Не заданы AVITO_CLIENT_ID и AVITO_CLIENT_SECRET")
        await self._rate_limit()
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
        if response.is_error:
            raise AvitoAPIError(
                f"OAuth Авито вернул {response.status_code}: {response.text[:300]}"
            )
        payload = response.json()
        self._token = payload["access_token"]
        self._token_expires_at = time.time() + int(payload.get("expires_in", 3600))
        return self._token

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Выполняет авторизованный запрос и преобразует ошибки API."""
        token = await self.get_access_token()
        await self._rate_limit()
        headers = {"Authorization": f"Bearer {token}", **kwargs.pop("headers", {})}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method, f"{self.api_base_url}{path}", headers=headers, **kwargs
            )
        if response.is_error:
            raise AvitoAPIError(
                f"Avito API вернул {response.status_code}: {response.text[:500]}"
            )
        return response.json()

    async def get_listings(
        self, user_id: int, *, page: int = 1, per_page: int = 100
    ) -> dict[str, Any]:
        """Получает объявления аккаунта через стандартный путь Core API.

        TODO: сверить доступный для договора Авито набор фильтров и версию метода
        `/core/v1/items` до первого продуктивного запуска.
        """
        return await self._request(
            "GET",
            "/core/v1/items",
            params={"user_id": user_id, "page": page, "per_page": per_page},
        )

    async def get_chats(self, user_id: int, *, limit: int = 100) -> dict[str, Any]:
        """Получает список диалогов мессенджера для аккаунта."""
        return await self._request(
            "GET", f"/messenger/v2/accounts/{user_id}/chats", params={"limit": limit}
        )

    async def get_messages(
        self, user_id: int, chat_id: str, *, limit: int = 100
    ) -> dict[str, Any]:
        """Получает сообщения конкретного диалога."""
        return await self._request(
            "GET",
            f"/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages",
            params={"limit": limit},
        )

    async def send_message(
        self, user_id: int, chat_id: str, text: str
    ) -> dict[str, Any]:
        """Отправляет текстовое сообщение от подключённого аккаунта."""
        if not text.strip():
            raise ValueError("Нельзя отправить пустое сообщение")
        return await self._request(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages",
            json={"message": {"text": text.strip(), "type": "text"}},
        )
