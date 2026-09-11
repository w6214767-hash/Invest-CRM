"""Critical user flows: durable import, finance, purchase gates and session boundaries."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.core.db import get_session
from app.investscan.auth import safe_next
from app.investscan.finance import calculate
from app.investscan.schemas import FinanceInput
from app.main import app
from app.models.investscan import Identity, LoginSession, now

PREFIX = "/api/v1/investscan"
ITEM = {
    "title": "Участок для проверки",
    "asset_type": "land",
    "district": "Домодедово",
    "area": 10,
    "asking_price": 3_000_000,
    "land_use": "ИЖС",
    "source": "file",
    "external_id": "lot-100",
}
FINANCE = {
    "object_version": 1,
    "resale_price": 5_000_000,
    "purchase_price": 3_000_000,
    "repairs": 200_000,
    "legal_costs": 50_000,
    "other_costs": 100_000,
    "reserve": 150_000,
    "target_profit": 600_000,
    "holding_months": 3,
    "monthly_holding": 30_000,
    "annual_finance_pct": 24,
    "financed_share_pct": 50,
    "sale_cost_pct": 2,
    "acquisition_cost_pct": 1,
    "resale_basis": "Учебный расчёт по проверенным аналогам",
}


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = db
    monkeypatch.setattr(settings, "investscan_dev_auth", True)
    with TestClient(app) as client:
        client.engine = engine
        assert client.post(PREFIX + "/auth/development").status_code == 204
        me = client.get(PREFIX + "/auth/me").json()
        client.headers["X-CSRF-Token"] = me["csrf_token"]
        yield client
    app.dependency_overrides.clear()
    engine.dispose()


def create(client, **changes):
    result = client.post(PREFIX + "/objects", json={**ITEM, **changes})
    assert result.status_code == 201, result.text
    return result.json()["object"]


def change_stage(client, obj, stage):
    return client.patch(
        f"{PREFIX}/objects/{obj['id']}",
        json={
            "version": obj["version"],
            "stage": stage,
            "reason": "Проверено собственником",
        },
    )


def test_finance_solves_purchase_dependent_costs():
    results = calculate(FinanceInput(**FINANCE))
    assert results["financing_cost"] == 90_000
    assert results["total_cost"] == 3_810_000
    assert results["profit"] == 1_190_000
    assert results["max_buyout_price"] == 3_567_307
    assert results["scenarios"]["stress"]["resale_price"] == 4_500_000
    assert results["scenarios"]["stress"]["profit"] == 700_000
    assert results["scenarios"]["upside"]["profit"] == 1_680_000


def test_no_viable_buyout_is_zero_not_negative():
    result = calculate(FinanceInput(**{**FINANCE, "target_profit": 10_000_000}))
    assert result["max_buyout_price"] == 0
    assert result["headroom"] < 0


def test_import_idempotent_and_tracks_changed_price(client):
    path = PREFIX + "/imports"
    first = client.post(path, json={"items": [ITEM]}).json()
    assert first["created"] == 1
    assert client.post(path, json={"items": [ITEM]}).json()["unchanged"] == 1
    assert (
        client.post(path, json={"items": [{**ITEM, "asking_price": 2_800_000}]}).json()[
            "updated"
        ]
        == 1
    )
    objects = client.get(PREFIX + "/objects").json()
    assert objects["total"] == 1
    obj = objects["items"][0]
    detail = client.get(f"{PREFIX}/objects/{obj['id']}").json()
    assert obj["asking_price"] == 2_800_000
    assert [p["price"] for p in detail["prices"]] == [2_800_000, 3_000_000]
    assert len(detail["sources"]) == 1


def test_invalid_batch_does_not_partially_import(client):
    response = client.post(
        PREFIX + "/imports",
        json={"items": [ITEM, {**ITEM, "external_id": "bad", "asking_price": -10}]},
    )
    assert response.status_code == 422
    assert client.get(PREFIX + "/objects").json()["total"] == 0


def test_cross_source_duplicates_require_review(client):
    a = create(client, cadastral_number="50:28:000:123")
    create(client, source="avito", cadastral_number="50:28:000:123")
    detail = client.get(f"{PREFIX}/objects/{a['id']}").json()
    assert len(detail["possible_duplicates"]) == 1
    assert detail["market"]["count"] == 0


def test_no_self_comparison_and_no_market_price_without_three_comps(client):
    obj = create(client)
    assert (
        client.get(f"{PREFIX}/objects/{obj['id']}").json()["market"]["estimated_price"]
        is None
    )
    for index, price in enumerate([4_000_000, 4_500_000, 5_000_000]):
        create(client, external_id=f"comp-{index}", asking_price=price)
    market = client.get(f"{PREFIX}/objects/{obj['id']}").json()["market"]
    assert market["count"] == 3
    assert market["estimated_price"] == 4_500_000


def test_version_conflict_and_stale_evaluation(client):
    obj = create(client)
    assert (
        client.post(
            f"{PREFIX}/objects/{obj['id']}/evaluations", json=FINANCE
        ).status_code
        == 201
    )
    update = client.patch(
        f"{PREFIX}/objects/{obj['id']}", json={"version": 1, "asking_price": 2_900_000}
    )
    assert update.status_code == 200
    assert (
        client.patch(
            f"{PREFIX}/objects/{obj['id']}",
            json={"version": 1, "asking_price": 2_700_000},
        ).status_code
        == 409
    )
    assert (
        client.get(f"{PREFIX}/objects/{obj['id']}").json()["evaluation_stale"] is True
    )
    assert (
        client.post(
            f"{PREFIX}/objects/{obj['id']}/evaluations", json=FINANCE
        ).status_code
        == 409
    )


def test_purchase_requires_checks_calculation_and_owner(client):
    obj = create(client)
    obj = change_stage(client, obj, "review").json()
    assert change_stage(client, obj, "approval").status_code == 409
    checks = client.get(f"{PREFIX}/objects/{obj['id']}").json()["checks"]
    for check in checks:
        path = f"{PREFIX}/objects/{obj['id']}/checks/{check['code']}"
        assert (
            client.put(path, json={"status": "passed", "evidence": ""}).status_code
            == 422
        )
        assert (
            client.put(
                path,
                json={"status": "passed", "evidence": "Проверка документа 06.09.2026"},
            ).status_code
            == 200
        )
    assert change_stage(client, obj, "approval").status_code == 409
    client.post(
        f"{PREFIX}/objects/{obj['id']}/evaluations",
        json={**FINANCE, "object_version": obj["version"]},
    )
    response = change_stage(client, obj, "approval")
    assert response.status_code == 200, response.text
    obj = response.json()
    with Session(client.engine) as db:
        identity = db.exec(select(Identity)).first()
        identity.role = "analyst"
        db.add(identity)
        db.commit()
    assert change_stage(client, obj, "bought").status_code == 403
    with Session(client.engine) as db:
        identity = db.exec(select(Identity)).first()
        identity.role = "owner"
        db.add(identity)
        db.commit()
    assert change_stage(client, obj, "bought").status_code == 200


def test_stage_gate_cannot_be_bypassed_by_changing_price_same_request(client):
    obj = create(client)
    obj = change_stage(client, obj, "review").json()
    result = client.patch(
        f"{PREFIX}/objects/{obj['id']}",
        json={
            "version": obj["version"],
            "stage": "approval",
            "asking_price": 1,
            "reason": "Попытка обхода",
        },
    )
    assert result.status_code == 409


def test_csrf_roles_logout_and_expiry(client):
    csrf = client.headers.pop("X-CSRF-Token")
    assert client.post(PREFIX + "/objects", json=ITEM).status_code == 403
    client.headers["X-CSRF-Token"] = csrf
    with Session(client.engine) as db:
        user = db.exec(select(Identity)).first()
        user.role = "viewer"
        db.add(user)
        db.commit()
    assert client.post(PREFIX + "/objects", json=ITEM).status_code == 403
    assert client.get(PREFIX + "/objects").status_code == 200
    with Session(client.engine) as db:
        login = db.exec(select(LoginSession)).first()
        login.expires_at = now() - timedelta(seconds=1)
        db.add(login)
        db.commit()
    assert client.get(PREFIX + "/objects").status_code == 401
    client.post(PREFIX + "/auth/development")
    client.headers["X-CSRF-Token"] = client.get(PREFIX + "/auth/me").json()[
        "csrf_token"
    ]
    assert client.post(PREFIX + "/auth/logout").status_code == 204
    assert client.get(PREFIX + "/objects").status_code == 401


def test_anonymous_cannot_read_workspace():
    with TestClient(app) as anonymous:
        for path in [
            "/objects",
            "/sources",
            "/overview",
            "/buyers",
            "/tasks",
            "/searches",
        ]:
            assert anonymous.get(PREFIX + path).status_code == 401


def test_dev_login_disabled_by_default(client, monkeypatch):
    monkeypatch.setattr(settings, "investscan_dev_auth", False)
    assert client.post(PREFIX + "/auth/development").status_code == 404
    assert client.get(PREFIX + "/auth/login").status_code == 503


@pytest.mark.parametrize(
    "target", ["//evil.test", "https://evil.test", "/\\evil.test", "/\n/evil.test"]
)
def test_redirect_allowlist(target):
    assert safe_next(target) == "/"


def test_filters_and_buyer_matching(client):
    obj = create(client, urgency_evidence="Продавец сообщил срок 10 дней")
    create(client, external_id="no-urgency", district="Чехов", asking_price=4_000_000)
    assert (
        client.get(PREFIX + "/objects?urgent=true&max_price=3500000").json()["total"]
        == 1
    )
    assert client.get(PREFIX + "/objects?district=Чехов").json()["total"] == 1
    assert (
        client.post(
            PREFIX + "/buyers",
            json={
                "name": "Тестовый покупатель",
                "asset_type": "land",
                "districts": ["Домодедово"],
                "max_budget": 3_100_000,
                "min_area": 8,
                "max_area": 12,
            },
        ).status_code
        == 201
    )
    assert len(client.get(f"{PREFIX}/objects/{obj['id']}").json()["buyers"]) == 1
    profile = client.post(
        PREFIX + "/searches",
        json={"name": "Срочный выкуп", "filters": {"urgent": True}},
    )
    assert profile.status_code == 201
    assert client.get(PREFIX + "/searches").json()[0]["filters"]["urgent"] is True
    assert client.get(PREFIX + "/overview").json()["urgent"] == 1


def test_invalid_filter_range_returns_validation_error(client):
    assert client.get(PREFIX + "/objects?min_price=100&max_price=1").status_code == 422


@pytest.mark.parametrize(
    "roles,audience,expected,owner_subject,amr",
    [
        (["analyst"], "investscan-test", 303, "", []),
        ([], "investscan-test", 403, "", []),
        (["owner"], "wrong-client", 303, "", []),
        ([], "investscan-test", 303, "user-42", ["pwd", "otp", "mfa"]),
        (["owner"], "investscan-test", 403, "user-42", ["pwd"]),
        (["owner"], "investscan-test", 403, "other", ["pwd", "otp", "mfa"]),
    ],
)
def test_oidc_code_pkce_signed_token_and_module_roles(
    client, monkeypatch, roles, audience, expected, owner_subject, amr
):
    """Exercise Authlib against a local in-process provider, including real RSA signatures."""
    import base64
    import hashlib
    import time
    from urllib.parse import parse_qs, urlsplit

    import httpx
    from authlib.integrations.starlette_client import OAuth
    from authlib.jose import JsonWebKey, jwt

    from app.investscan import auth

    issuer = "https://identity.example.test"
    key = JsonWebKey.generate_key(
        "RSA", 2048, is_private=True, options={"kid": "test-key"}
    )
    flow = {}

    def provider(request):
        path = request.url.path
        if path == "/.well-known/openid-configuration":
            return httpx.Response(
                200,
                json={
                    "issuer": issuer,
                    "authorization_endpoint": issuer + "/authorize",
                    "token_endpoint": issuer + "/token",
                    "jwks_uri": issuer + "/jwks",
                    "id_token_signing_alg_values_supported": ["RS256"],
                },
            )
        if path == "/jwks":
            return httpx.Response(200, json={"keys": [key.as_dict(is_private=False)]})
        if path == "/token":
            body = parse_qs(request.content.decode())
            verifier = body["code_verifier"][0]
            challenge = (
                base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
                .rstrip(b"=")
                .decode()
            )
            assert challenge == flow["challenge"]
            assert body["code"] == ["one-time-test-code"]
            claims = {
                "iss": issuer,
                "sub": "user-42",
                "aud": audience,
                "iat": int(time.time()),
                "exp": int(time.time()) + 120,
                "nonce": flow["nonce"],
                "name": "SSO test",
                "investscan_roles": roles,
                "amr": amr,
            }
            signed = jwt.encode(
                {"alg": "RS256", "kid": "test-key"}, claims, key
            ).decode()
            return httpx.Response(
                200,
                json={
                    "access_token": "test-only",
                    "token_type": "Bearer",
                    "id_token": signed,
                },
            )
        raise AssertionError(path)

    registry = OAuth()
    registry.register(
        "shtab",
        client_id="investscan-test",
        client_secret="test-only-secret",
        server_metadata_url=issuer + "/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid profile",
            "code_challenge_method": "S256",
            "transport": httpx.MockTransport(provider),
        },
    )
    monkeypatch.setattr(auth, "oauth", registry)
    monkeypatch.setattr(settings, "oidc_owner_subject", owner_subject)
    monkeypatch.setattr(settings, "oidc_issuer", issuer)
    monkeypatch.setattr(settings, "oidc_client_id", "investscan-test")
    monkeypatch.setattr(settings, "oidc_client_secret", "test-only-secret")
    client.cookies.clear()
    redirect = client.get(
        PREFIX + "/auth/login?next=/objects/42", follow_redirects=False
    )
    assert redirect.status_code == 302
    query = parse_qs(urlsplit(redirect.headers["location"]).query)
    assert query["code_challenge_method"] == ["S256"]
    flow["challenge"] = query["code_challenge"][0]
    flow["nonce"] = query["nonce"][0]
    callback = client.get(
        PREFIX + "/auth/callback",
        params={"state": query["state"][0], "code": "one-time-test-code"},
        follow_redirects=False,
    )
    assert callback.status_code == expected, callback.text
    if audience == "wrong-client":
        assert callback.headers["location"] == "/login?error=sso"
        assert client.get(PREFIX + "/auth/me").status_code == 401
    elif expected == 303:
        assert callback.headers["location"] == "/objects/42"
        assert client.get(PREFIX + "/auth/me").json()["role"] == (
            "owner" if owner_subject else "analyst"
        )
        # The OAuth state cannot be replayed to create a second session.
        replay = client.get(
            PREFIX + "/auth/callback",
            params={"state": query["state"][0], "code": "one-time-test-code"},
            follow_redirects=False,
        )
        assert replay.headers["location"] == "/login?error=sso"
    else:
        assert client.get(PREFIX + "/auth/me").status_code == 401


def test_production_does_not_expose_legacy_registration_or_local_auth():
    import os
    import subprocess
    import sys

    code = """
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
assert c.post('/api/v1/auth/register', json={}).status_code == 404
assert c.post('/api/v1/investscan/auth/development').status_code == 404
assert c.get('/api/v1/investscan/objects').status_code == 401
assert c.get('/api/v1/listings').status_code == 404
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        env={
            **os.environ,
            "ENVIRONMENT": "production",
            "APP_URL": "https://invest.example.test",
            "SECRET_KEY": "test-only-production-check-secret-" * 3,
            "INVESTSCAN_DEV_AUTH": "false",
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_russian_search_is_case_insensitive(client):
    create(client)
    assert (
        client.get(PREFIX + "/objects?q=участок&district=домодедово").json()["total"]
        == 1
    )


@pytest.mark.parametrize(
    "subject,amr,roles,expected",
    [
        ("user-42", ["pwd", "otp", "mfa"], [], "owner"),
        ("user-42", ["pwd"], ["owner"], None),
        ("other-user", ["pwd", "otp", "mfa"], ["owner"], None),
        ("user-42", "mfa pwd otp", ["owner"], None),
        ("user-42", ["pwd", "otp", ["mfa"]], [], None),
    ],
)
def test_hq_owner_binding_requires_subject_and_mfa(
    monkeypatch, subject, amr, roles, expected
):
    monkeypatch.setattr(settings, "oidc_owner_subject", "user-42")
    monkeypatch.setattr(settings, "oidc_required_amr", "mfa pwd otp")
    from app.investscan import auth

    assert (
        auth.claims_role({"sub": subject, "amr": amr, "investscan_roles": roles})
        == expected
    )


def test_hq_owner_binding_rejects_existing_different_identity(client, monkeypatch):
    monkeypatch.setattr(settings, "oidc_owner_subject", "different-subject")
    assert client.get(PREFIX + "/objects").status_code == 403


def test_owner_mfa_pause_preserves_identity_boundary(monkeypatch):
    from app.investscan import auth

    monkeypatch.setattr(settings, "oidc_owner_subject", "user-42")
    monkeypatch.setattr(settings, "oidc_mfa_suspended", True)
    assert auth.claims_role({"sub": "user-42", "amr": ["pwd"]}) == "owner"
    assert auth.claims_role({"sub": "other", "amr": ["pwd"]}) is None
    assert auth.claims_role({"sub": "user-42", "amr": []}) is None
    assert auth.claims_role({"sub": "user-42", "amr": "pwd"}) is None
    paused_hash = auth.token_hash("opaque-test-token")
    monkeypatch.setattr(settings, "oidc_mfa_suspended", False)
    assert auth.token_hash("opaque-test-token") != paused_hash
    assert auth.claims_role({"sub": "user-42", "amr": ["pwd"]}) is None


def test_restoring_mfa_rejects_paused_session(client, monkeypatch):
    monkeypatch.setattr(settings, "oidc_mfa_suspended", True)
    assert client.post(PREFIX + "/auth/development").status_code == 204
    assert client.get(PREFIX + "/auth/me").status_code == 200
    monkeypatch.setattr(settings, "oidc_mfa_suspended", False)
    assert client.get(PREFIX + "/auth/me").status_code == 401
