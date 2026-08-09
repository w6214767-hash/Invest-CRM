"""Расписание заданий для запуска из внешнего планировщика или ARQ."""

from dataclasses import dataclass
from typing import Awaitable, Callable

from app.workers.tasks import (
    daily_digest,
    poll_chats,
    rescore_listings,
    sync_avito_listings,
)


@dataclass(frozen=True)
class ScheduledTask:
    """Описание периодического задания без привязки к конкретной очереди."""

    name: str
    cron: str
    handler: Callable[..., Awaitable[dict]]


SCHEDULED_TASKS = [
    ScheduledTask("sync_avito_listings", "*/15 * * * *", sync_avito_listings),
    ScheduledTask("rescore_listings", "0 */2 * * *", rescore_listings),
    ScheduledTask("poll_chats", "*/5 * * * *", poll_chats),
    ScheduledTask("daily_digest", "0 19 * * *", daily_digest),
]
