"""Расчёт инвестиционного скоринга участков и выявление рисков."""

from dataclasses import dataclass
from statistics import median
from typing import Iterable

URGENCY_PHRASES = ("срочно", "торг", "нужны деньги")
RED_FLAG_PATTERNS: dict[str, tuple[str, ...]] = {
    "Нет кадастрового номера": ("без кадастров", "кадастровый позже"),
    "Сомнительный статус документов": ("по расписке", "не оформлен", "без документов"),
    "Ограничения или обременения": ("обременен", "арест", "сервитут"),
    "Неподтверждённые коммуникации": ("свет рядом", "газ рядом", "в перспективе"),
}


@dataclass(frozen=True)
class ScoreBreakdown:
    """Детализация оценки для отображения в карточке лота."""

    discount_pct: float
    median_price_per_sotka: float
    score: float
    urgency_score: float
    red_flags: list[str]


def median_price_per_sotka(prices: Iterable[float]) -> float:
    """Вычисляет медиану цен за сотку по кластеру сопоставимых лотов."""
    valid_prices = [float(price) for price in prices if float(price) > 0]
    if not valid_prices:
        raise ValueError("Для оценки нужна хотя бы одна положительная цена за сотку")
    return float(median(valid_prices))


def calculate_discount_pct(price_per_sotka: float, cluster_median: float) -> float:
    """Возвращает дисконт объявления к медиане кластера в процентах."""
    if price_per_sotka <= 0 or cluster_median <= 0:
        raise ValueError("Цена за сотку и медиана должны быть положительными")
    return round((cluster_median - price_per_sotka) / cluster_median * 100, 2)


def calculate_score(
    discount_pct: float,
    liquidity: float,
    location: float,
    docs: float,
    utility: float,
    seller_urgency: float,
) -> float:
    """Считает итог по формуле инвестиционной модели в шкале от 0 до 100.

    Формула: 0.35×Discount + 0.20×Liquidity + 0.15×Location +
    0.10×Docs + 0.10×Utility + 0.10×SellerUrgency. Отрицательный
    дисконт не повышает оценку, а каждую компоненту ограничивает шкала 0–100.
    """
    components = (discount_pct, liquidity, location, docs, utility, seller_urgency)
    normalized = [min(100.0, max(0.0, float(value))) for value in components]
    score = (
        0.35 * normalized[0]
        + 0.20 * normalized[1]
        + 0.15 * normalized[2]
        + 0.10 * normalized[3]
        + 0.10 * normalized[4]
        + 0.10 * normalized[5]
    )
    return round(score, 2)


def detect_urgency(text: str) -> tuple[float, list[str]]:
    """Ищет маркеры срочной продажи и возвращает балл с найденными фразами."""
    normalized = text.casefold()
    matches = [phrase for phrase in URGENCY_PHRASES if phrase in normalized]
    score = min(100.0, len(matches) * 35.0)
    return score, matches


def detect_red_flags(text: str, cadastral_number: str | None = None) -> list[str]:
    """Отмечает текстовые признаки юридического и инфраструктурного риска."""
    normalized = text.casefold()
    flags = [
        label
        for label, patterns in RED_FLAG_PATTERNS.items()
        if any(pattern in normalized for pattern in patterns)
    ]
    if not cadastral_number:
        flags.append("Не указан кадастровый номер")
    return list(dict.fromkeys(flags))


def evaluate_listing(
    *,
    price_rub: int,
    area_sotka: float,
    cluster_prices_per_sotka: Iterable[float],
    description: str,
    liquidity: float,
    location: float,
    docs: float,
    utility: float,
    cadastral_number: str | None = None,
) -> ScoreBreakdown:
    """Собирает рыночную оценку, срочность, риски и итоговый балл объявления."""
    if price_rub <= 0 or area_sotka <= 0:
        raise ValueError("Цена и площадь должны быть положительными")
    current_price_per_sotka = price_rub / area_sotka
    market_median = median_price_per_sotka(cluster_prices_per_sotka)
    discount_pct = calculate_discount_pct(current_price_per_sotka, market_median)
    urgency_score, _ = detect_urgency(description)
    score = calculate_score(
        discount_pct, liquidity, location, docs, utility, urgency_score
    )
    return ScoreBreakdown(
        discount_pct=discount_pct,
        median_price_per_sotka=market_median,
        score=score,
        urgency_score=urgency_score,
        red_flags=detect_red_flags(description, cadastral_number),
    )
