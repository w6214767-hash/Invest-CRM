"""Дымовой тест доступности приложения."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    """Эндпоинт здоровья отвечает без подключения к внешним сервисам."""
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "investscan"


def test_health_identifies_configured_release(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "investscan_release_sha", "a" * 40)
    assert TestClient(app).get("/health").json()["release"] == "a" * 40
