"""OIDC code + PKCE; opaque revocable DB sessions and explicit module roles."""

import hashlib
import secrets
from datetime import timedelta
from typing import Annotated
from urllib.parse import urlsplit

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import delete
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.config import settings
from app.models.investscan import Identity, LoginSession, now

router = APIRouter(prefix="/investscan/auth", tags=["Единый вход"])
COOKIE = "investscan_session"
oauth = OAuth()
if settings.oidc_issuer and settings.oidc_client_id:
    oauth.register(
        "shtab",
        client_id=settings.oidc_client_id,
        client_secret=settings.oidc_client_secret,
        server_metadata_url=settings.oidc_issuer.rstrip("/")
        + "/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile", "code_challenge_method": "S256"},
    )


def configured():
    return bool(
        settings.oidc_issuer and settings.oidc_client_id and settings.oidc_client_secret
    )


def local_auth():
    return settings.environment == "development" and settings.investscan_dev_auth


def token_hash(token):
    prefix = "mfa-suspended:" if settings.oidc_mfa_suspended else ""
    return hashlib.sha256((prefix + token).encode()).hexdigest()


def safe_next(value: str) -> str:
    parsed = urlsplit(value)
    if (
        not value.startswith("/")
        or value.startswith("//")
        or parsed.scheme
        or parsed.netloc
        or "\\" in value
        or any(ord(c) < 32 for c in value)
    ):
        return "/"
    return value


def claims_role(claims):
    if settings.oidc_owner_subject:
        required = (
            {"pwd"}
            if settings.oidc_mfa_suspended
            else set(settings.oidc_required_amr.split())
        )
        amr = claims.get("amr")
        if not settings.oidc_mfa_suspended and not {"mfa", "pwd", "otp"}.issubset(required):
            return None
        if (
            claims.get("sub") != settings.oidc_owner_subject
            or not isinstance(amr, list)
            or not all(isinstance(value, str) for value in amr)
            or not required.issubset(amr)
        ):
            return None
        return "owner"
    roles = claims.get(settings.oidc_roles_claim, [])
    roles = roles if isinstance(roles, list) else []
    return next((r for r in ("owner", "analyst", "viewer") if r in roles), None)


def current_identity(request: Request, session: SessionDep) -> Identity:
    token = request.cookies.get(COOKIE, "")
    record = session.get(LoginSession, token_hash(token)) if token else None
    if not record or record.expires_at <= now():
        raise HTTPException(401, "Войдите через Штаб")
    identity = session.get(Identity, record.identity_id)
    if (
        not identity
        or not identity.active
        or identity.role not in {"owner", "analyst", "viewer"}
    ):
        raise HTTPException(403, "Доступ к ИнвестСкану закрыт")
    if settings.oidc_owner_subject and (
        identity.issuer != settings.oidc_issuer
        or identity.subject != settings.oidc_owner_subject
        or identity.role != "owner"
    ):
        raise HTTPException(403, "Доступ разрешён только собственнику Штаба")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        supplied = request.headers.get("X-CSRF-Token", "")
        if not secrets.compare_digest(supplied, record.csrf_token):
            raise HTTPException(403, "Обновите страницу и повторите действие")
    request.state.csrf_token = record.csrf_token
    return identity


CurrentIdentity = Annotated[Identity, Depends(current_identity)]


def writer(identity: CurrentIdentity) -> Identity:
    if identity.role not in {"owner", "analyst"}:
        raise HTTPException(403, "Для изменения нужны права аналитика")
    return identity


Writer = Annotated[Identity, Depends(writer)]


def issue_session(session, identity, response, request):
    old = request.cookies.get(COOKIE)
    if old:
        session.exec(
            delete(LoginSession).where(LoginSession.token_hash == token_hash(old))
        )
    session.exec(delete(LoginSession).where(LoginSession.expires_at <= now()))
    raw = secrets.token_urlsafe(48)
    record = LoginSession(
        token_hash=token_hash(raw),
        identity_id=identity.id,
        csrf_token=secrets.token_urlsafe(32),
        expires_at=now() + timedelta(minutes=settings.session_minutes),
    )
    session.add(record)
    session.commit()
    response.set_cookie(
        COOKIE,
        raw,
        httponly=True,
        secure=settings.environment != "development",
        samesite="lax",
        max_age=settings.session_minutes * 60,
        path="/",
    )
    return response


@router.get("/config")
def auth_config():
    return {
        "sso_configured": configured(),
        "dev_auth": local_auth(),
        "shtab_url": settings.shtab_url,
    }


@router.get("/login")
async def start_login(request: Request, next: str = "/"):
    if not configured():
        raise HTTPException(503, "Единый вход ещё не подключён к Штабу")
    request.session.clear()
    request.session["next"] = safe_next(next)
    client = oauth.create_client("shtab")
    return await client.authorize_redirect(
        request, settings.app_url.rstrip("/") + "/api/v1/investscan/auth/callback"
    )


@router.get("/callback")
async def callback(request: Request, session: SessionDep):
    if not configured():
        raise HTTPException(503, "Единый вход не настроен")
    try:
        token = await oauth.create_client("shtab").authorize_access_token(request)
        claims = token[
            "userinfo"
        ]  # Authlib validates signature, issuer, audience and nonce.
    except Exception:
        request.session.clear()
        return RedirectResponse("/login?error=sso", status_code=303)
    if claims.get("iss") != settings.oidc_issuer or not claims.get("sub"):
        raise HTTPException(403, "Неверный источник учётной записи")
    role = claims_role(claims)
    identity = session.exec(
        select(Identity).where(
            Identity.issuer == claims["iss"], Identity.subject == claims["sub"]
        )
    ).first()
    if identity and not identity.active:
        raise HTTPException(403, "Доступ отключён администратором")
    if not role:
        if identity:
            session.exec(
                delete(LoginSession).where(LoginSession.identity_id == identity.id)
            )
            session.commit()
        request.session.clear()
        raise HTTPException(
            403, "Учётная запись или второй фактор не разрешены для ИнвестСкана"
        )
    if not identity:
        identity = Identity(
            issuer=claims["iss"],
            subject=claims["sub"],
            name=str(claims.get("name") or "Пользователь")[:255],
            role=role,
        )
    identity.role = role
    session.add(identity)
    session.flush()
    target = safe_next(request.session.pop("next", "/"))
    request.session.clear()
    return issue_session(
        session, identity, RedirectResponse(target, status_code=303), request
    )


@router.post("/development")
def dev_login(request: Request, session: SessionDep):
    if not local_auth():
        raise HTTPException(404, "Не найдено")
    # Explicit opt-in, development only. Never enable on an exposed server.
    identity = session.exec(
        select(Identity).where(
            Identity.issuer == "local-development", Identity.subject == "developer"
        )
    ).first()
    if not identity:
        identity = Identity(
            issuer="local-development",
            subject="developer",
            name="Локальная разработка",
            role="owner",
        )
        session.add(identity)
        session.flush()
    return issue_session(session, identity, Response(status_code=204), request)


@router.get("/me")
def me(request: Request, identity: CurrentIdentity):
    return {
        "id": identity.id,
        "name": identity.name,
        "role": identity.role,
        "csrf_token": request.state.csrf_token,
    }


@router.post("/logout")
def logout(request: Request, session: SessionDep, identity: CurrentIdentity):
    session.exec(
        delete(LoginSession).where(
            LoginSession.token_hash == token_hash(request.cookies[COOKIE])
        )
    )
    session.commit()
    response = Response(status_code=204)
    response.delete_cookie(COOKIE, path="/")
    request.session.clear()
    return response


@router.post("/revoke/{identity_id}")
def revoke(identity_id: int, session: SessionDep, identity: CurrentIdentity):
    if identity.role != "owner":
        raise HTTPException(403, "Нужны права собственника")
    target = session.get(Identity, identity_id)
    if not target:
        raise HTTPException(404, "Пользователь не найден")
    target.active = False
    session.add(target)
    session.exec(delete(LoginSession).where(LoginSession.identity_id == identity_id))
    session.commit()
    return {"revoked": True}
