"""Проверяет, что бизнес-маршруты API требуют авторизации по JWT."""

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.main import app


def _client_with_fresh_db() -> TestClient:
    """Создаёт тестовый клиент с изолированной in-memory базой."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_protected_endpoints_reject_anonymous_requests() -> None:
    """Без токена бизнес-данные CRM недоступны."""
    client = _client_with_fresh_db()
    try:
        for path in (
            "/api/v1/listings",
            "/api/v1/sellers",
            "/api/v1/deals",
            "/api/v1/offers",
            "/api/v1/negotiation",
            "/api/v1/analytics/dashboard",
            "/api/v1/integrations/overview",
        ):
            response = client.get(path)
            assert response.status_code == 401, path
    finally:
        app.dependency_overrides.clear()


def test_protected_endpoint_accepts_valid_token() -> None:
    """С валидным Bearer-токеном маршрут отдаёт данные как обычно."""
    client = _client_with_fresh_db()
    try:
        register = client.post(
            "/api/v1/auth/register",
            json={
                "email": "manager@test.local",
                "full_name": "Тестовый менеджер",
                "password": "supersecret1",
            },
        )
        assert register.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "manager@test.local", "password": "supersecret1"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        response = client.get(
            "/api/v1/listings", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
