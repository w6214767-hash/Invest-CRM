"""API профилей поиска, источников и аудита автоматизации."""

from datetime import datetime

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import IntegrationRun, Listing, SearchProfile
from app.schemas.integrations import (
    AgentAuditRead,
    IntegrationOverview,
    IntegrationSourceRead,
    ReviewListingRead,
    RunResult,
    SearchProfilePayload,
    SearchProfileRead,
)

router = APIRouter(prefix="/integrations", tags=["Интеграции"])


def get_or_create_profile(session: SessionDep) -> SearchProfile:
    profile = session.exec(select(SearchProfile).where(SearchProfile.is_active)).first()
    if profile:
        return profile
    profile = SearchProfile(
        districts=["Домодедово", "Ступино", "Чехов", "Подольск"],
        land_use=["ИЖС", "ЛПХ"],
        exclude_words=["аренда", "доля", "переуступка"],
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def source_statuses() -> list[IntegrationSourceRead]:
    return [
        IntegrationSourceRead(
            id="avito",
            name="Авито",
            status="online" if settings.avito_client_id else "setup",
            configured=bool(settings.avito_client_id),
        ),
        IntegrationSourceRead(
            id="domclick", name="Домклик", status="setup", configured=False
        ),
        IntegrationSourceRead(
            id="yandex", name="Яндекс Недвижимость", status="setup", configured=False
        ),
    ]


@router.get("/overview", response_model=IntegrationOverview)
def overview(session: SessionDep, current_user: CurrentUser) -> IntegrationOverview:
    profile = get_or_create_profile(session)
    listings = list(session.exec(select(Listing)).all())
    review = [item for item in listings if item.red_flags or not item.cadastral_number]
    runs = list(
        session.exec(
            select(IntegrationRun).order_by(IntegrationRun.created_at.desc()).limit(20)
        ).all()
    )
    qualified = [
        item for item in listings if (item.discount_pct or 0) >= profile.min_discount
    ]
    return IntegrationOverview(
        sources=source_statuses(),
        profile=SearchProfileRead.model_validate(profile),
        review_queue=[
            ReviewListingRead(
                id=item.id,
                title=item.title,
                score=item.score,
                red_flags=item.red_flags
                or (
                    ["Не указан кадастровый номер"] if not item.cadastral_number else []
                ),
            )
            for item in review
        ],
        audit=[
            AgentAuditRead(
                id=run.id,
                created_at=run.created_at,
                actor=run.actor,
                action=run.details.get("action", "Запуск поиска завершён"),
                details=run.details,
            )
            for run in runs
        ],
        metrics={
            "listings": len(listings),
            "qualified": len(qualified),
            "review": len(review),
            "runs": len(runs),
        },
    )


@router.put("/profile", response_model=SearchProfileRead)
def update_profile(
    payload: SearchProfilePayload, session: SessionDep, current_user: CurrentUser
) -> SearchProfile:
    profile = get_or_create_profile(session)
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.post("/run", response_model=RunResult)
def run_search(session: SessionDep, current_user: CurrentUser) -> RunResult:
    profile = get_or_create_profile(session)
    listings = list(session.exec(select(Listing)).all())
    matching = [
        item
        for item in listings
        if profile.min_price <= item.price_rub <= profile.max_price
        and profile.min_area <= item.area_sotka <= profile.max_area
    ]
    qualified = [
        item for item in matching if (item.discount_pct or 0) >= profile.min_discount
    ]
    review = [item for item in matching if item.red_flags or not item.cadastral_number]
    run = IntegrationRun(
        profile_id=profile.id,
        imported_count=len(matching),
        qualified_count=len(qualified),
        review_count=len(review),
        actor="manager",
        details={
            "action": "Профиль поиска обработан",
            "profile": profile.name,
            "completed_at": datetime.utcnow().isoformat(),
        },
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return RunResult(
        run_id=run.id,
        imported_count=run.imported_count,
        qualified_count=run.qualified_count,
        duplicates_count=run.duplicates_count,
        review_count=run.review_count,
    )
