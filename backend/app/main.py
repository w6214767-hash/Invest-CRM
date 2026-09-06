"""Точка входа FastAPI-приложения инвестиционной CRM."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import text
from sqlmodel import Session
from app.core.db import engine
from starlette.middleware.sessions import SessionMiddleware
from app.investscan import auth as scan_auth, routes as scan_routes
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name, version="0.2.0", docs_url="/docs", redoc_url="/redoc"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.environment != "development":
    if (
        len(settings.secret_key) < 40
        or "секрет" in settings.secret_key
        or "замен" in settings.secret_key
        or "replace-with" in settings.secret_key
    ):
        raise RuntimeError(
            "Production requires a random SECRET_KEY of at least 40 characters"
        )
    if settings.investscan_dev_auth:
        raise RuntimeError("Development auth is forbidden outside development")
    if not settings.app_url.startswith("https://"):
        raise RuntimeError("Production APP_URL must use HTTPS")
    if settings.oidc_issuer and not settings.oidc_issuer.startswith("https://"):
        raise RuntimeError("Production OIDC issuer must use HTTPS")
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="investscan_oauth",
    max_age=600,
    same_site="lax",
    https_only=settings.environment != "development",
)
# Legacy endpoints only exist in local development. Production uses the new identity boundary.
if settings.environment == "development":
    app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(scan_auth.router, prefix=settings.api_v1_prefix)
app.include_router(scan_routes.router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health", tags=["Система"])
def health() -> dict[str, str]:
    """Возвращает состояние процесса без зависимости от внешних сервисов."""
    return {
        "status": "ok",
        "service": "investscan",
        "environment": settings.environment,
        "release": settings.investscan_release_sha,
    }


@app.get("/ready", tags=["Система"])
def ready():
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1 FROM is_objects LIMIT 1"))
    except Exception:
        raise HTTPException(503, "База данных или схема недоступна")
    return {"status": "ready", "service": "investscan"}


@app.exception_handler(ValidationError)
async def invalid_model(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(
                include_url=False, include_context=False, include_input=False
            )
        },
    )
