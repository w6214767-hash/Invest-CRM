"""Простой процесс воркера для Docker без жёсткой привязки к брокеру."""

import asyncio
import logging

from app.workers.tasks import rescore_listings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def run() -> None:
    """Периодически запускает безопасный локальный пересчёт скоринга."""
    while True:
        try:
            result = await rescore_listings()
            logger.info("Пересчёт скоринга завершён: %s", result)
        except Exception:
            logger.exception("Не удалось выполнить пересчёт скоринга")
        await asyncio.sleep(7200)


if __name__ == "__main__":
    asyncio.run(run())
