"""Проверки формулы инвестиционного скоринга."""

import pytest

from app.services.scoring import (
    calculate_discount_pct,
    calculate_score,
    evaluate_listing,
    median_price_per_sotka,
)


def test_median_price_per_sotka_for_even_cluster() -> None:
    """Медиана чётного числа сопоставимых цен считается корректно."""
    assert median_price_per_sotka([100_000, 120_000, 180_000, 200_000]) == 150_000


def test_discount_and_exact_weighted_score() -> None:
    """Итог совпадает с заданной формулой весов."""
    discount = calculate_discount_pct(70_000, 100_000)
    assert discount == 30.0
    assert calculate_score(discount, 80, 60, 90, 50, 70) == 56.5


def test_score_caps_negative_discount_and_components() -> None:
    """Дорогой лот не получает бонуса за отрицательный дисконт."""
    assert calculate_score(-25, 150, 100, 100, 100, 100) == 65.0


def test_evaluate_listing_detects_urgency_and_flags() -> None:
    """Оценка распознаёт маркеры срочности и отсутствие кадастра."""
    result = evaluate_listing(
        price_rub=700_000,
        area_sotka=10,
        cluster_prices_per_sotka=[90_000, 100_000, 110_000],
        description="Срочно, возможен торг, нужны деньги. Свет рядом.",
        liquidity=80,
        location=70,
        docs=60,
        utility=50,
    )
    assert result.discount_pct == 30.0
    assert result.urgency_score == 100.0
    assert "Не указан кадастровый номер" in result.red_flags
    assert "Неподтверждённые коммуникации" in result.red_flags


def test_invalid_cluster_is_rejected() -> None:
    """Пустой набор компсов не скрывает ошибку оценки."""
    with pytest.raises(ValueError):
        median_price_per_sotka([])
