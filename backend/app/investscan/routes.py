"""InvestScan API. All workspace data is server-persisted and module-authorized."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.api.deps import SessionDep
from app.investscan.auth import CurrentIdentity, Writer
from app.investscan.finance import calculate
from app.investscan.schemas import (
    BuyerInput,
    CheckInput,
    FilterInput,
    FinanceInput,
    ImportPayload,
    NoteInput,
    ObjectInput,
    ObjectUpdate,
    SearchInput,
    TaskInput,
    TaskUpdate,
)
from app.investscan.service import (
    audit,
    bump,
    comparable_market,
    get_object,
    ingest,
    latest_evaluation,
    match_buyers,
    stage_gate,
)
from app.models.investscan import (
    Activity,
    Buyer,
    Check,
    Evaluation,
    ImportRun,
    Object,
    PriceObservation,
    Search,
    SourceListing,
    WorkTask,
    now,
)

router = APIRouter(prefix="/investscan", tags=["ИнвестСкан"])


def object_query(filters):
    query = select(Object)
    if filters.q:
        pattern = f"%{filters.q}%"
        query = query.where(
            Object.title.ilike(pattern)
            | Object.address.ilike(pattern)
            | Object.cadastral_number.ilike(pattern)
        )
    for field in ("asset_type", "stage"):
        value = getattr(filters, field)
        if value:
            query = query.where(getattr(Object, field) == value)
    if filters.district:
        query = query.where(Object.district.ilike(f"%{filters.district}%"))
    query = query.where(
        Object.asking_price >= filters.min_price, Object.area >= filters.min_area
    )
    if filters.max_price:
        query = query.where(Object.asking_price <= filters.max_price)
    if filters.max_area:
        query = query.where(Object.area <= filters.max_area)
    if filters.urgent:
        query = query.where(Object.urgency_evidence != "")
    if filters.starred:
        query = query.where(Object.starred)
    for word in filters.exclude.split(","):
        if word.strip():
            query = query.where(
                ~Object.description.ilike(f"%{word.strip()}%"),
                ~Object.title.ilike(f"%{word.strip()}%"),
            )
    return query


@router.get("/objects")
def objects(
    session: SessionDep,
    identity: CurrentIdentity,
    filters: FilterInput = Depends(),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    query = object_query(filters)
    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    items = session.exec(
        query.order_by(
            Object.starred.desc(), Object.updated_at.desc(), Object.id.desc()
        )
        .offset(offset)
        .limit(limit)
    ).all()
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/objects", status_code=201)
def create_object(payload: ObjectInput, session: SessionDep, identity: Writer):
    try:
        obj, status = ingest(session, payload, identity.name)
        session.commit()
        session.refresh(obj)
        return {"object": obj, "status": status}
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Источник уже импортируется. Повторите запрос")


@router.post("/imports", status_code=201)
def import_objects(payload: ImportPayload, session: SessionDep, identity: Writer):
    counts = {"created": 0, "updated": 0, "unchanged": 0}
    try:
        for item in payload.items:
            _, status = ingest(session, item, identity.name)
            counts[status] += 1
        run = ImportRun(author=identity.name, **counts)
        session.add(run)
        audit(
            session,
            None,
            "import",
            f"Импорт: новых {counts['created']}, ценовых изменений {counts['updated']}, без изменений {counts['unchanged']}",
            identity.name,
        )
        session.commit()
        session.refresh(run)
        return run
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            409, "Конфликт параллельного импорта. Пакет не сохранён; повторите"
        )


@router.get("/objects/{object_id}")
def detail(object_id: int, session: SessionDep, identity: CurrentIdentity):
    obj = get_object(session, object_id)
    evaluation = latest_evaluation(session, object_id)
    duplicates = (
        session.exec(
            select(Object).where(
                Object.id != object_id, Object.cadastral_number == obj.cadastral_number
            )
        ).all()
        if obj.cadastral_number
        else []
    )
    return {
        "object": obj,
        "sources": session.exec(
            select(SourceListing).where(SourceListing.object_id == object_id)
        ).all(),
        "prices": session.exec(
            select(PriceObservation)
            .where(PriceObservation.object_id == object_id)
            .order_by(PriceObservation.id.desc())
            .limit(100)
        ).all(),
        "checks": session.exec(
            select(Check).where(Check.object_id == object_id).order_by(Check.id)
        ).all(),
        "activities": session.exec(
            select(Activity)
            .where(Activity.object_id == object_id)
            .order_by(Activity.id.desc())
            .limit(100)
        ).all(),
        "tasks": session.exec(
            select(WorkTask).where(WorkTask.object_id == object_id)
        ).all(),
        "evaluation": evaluation,
        "evaluation_stale": bool(
            evaluation and evaluation.object_version != obj.version
        ),
        "market": comparable_market(session, obj),
        "buyers": match_buyers(session, obj),
        "possible_duplicates": duplicates,
    }


@router.patch("/objects/{object_id}")
def update_object(
    object_id: int, payload: ObjectUpdate, session: SessionDep, identity: Writer
):
    obj = get_object(session, object_id, lock=True)
    values = payload.model_dump(exclude_unset=True, exclude={"version", "reason"})
    if any(v is None for v in values.values()):
        raise HTTPException(422, "Поля изменения не могут быть пустыми")
    if not values:
        return obj
    new_stage = values.get("stage")
    if new_stage and new_stage != obj.stage:
        if len(payload.reason) < 3:
            raise HTTPException(422, "Укажите основание перехода")
        if new_stage in {"approval", "bought"} and any(
            k in values for k in {"asking_price", "title", "urgency_evidence"}
        ):
            raise HTTPException(
                409, "Сначала сохраните данные и пересчитайте экономику"
            )
        stage_gate(session, obj, new_stage, identity)
    if "asking_price" in values and values["asking_price"] != obj.asking_price:
        session.add(PriceObservation(object_id=obj.id, price=values["asking_price"]))
    # Pinning and stage changes do not alter financial assumptions; carry valuation version.
    evaluation = latest_evaluation(session, obj.id)
    carry = (
        evaluation
        and evaluation.object_version == obj.version
        and set(values) <= {"stage", "starred"}
    )
    bump(session, obj, payload.version, values)
    if carry:
        # Keep immutable valuation: copy, retaining inputs and the original author.
        session.add(
            Evaluation(
                object_id=obj.id,
                object_version=obj.version,
                inputs=evaluation.inputs,
                results=evaluation.results,
                author=evaluation.author,
            )
        )
    audit(
        session,
        obj.id,
        "stage" if new_stage else "updated",
        (
            f"Этап: {new_stage}. "
            if new_stage
            else "Изменено: " + ", ".join(values) + ". "
        )
        + payload.reason,
        identity.name,
    )
    session.commit()
    session.refresh(obj)
    return obj


@router.post("/objects/{object_id}/evaluations", status_code=201)
def evaluate(
    object_id: int, payload: FinanceInput, session: SessionDep, identity: Writer
):
    obj = get_object(session, object_id, lock=True)
    if payload.object_version != obj.version:
        raise HTTPException(409, "Данные объекта изменились. Обновите расчёт")
    result = Evaluation(
        object_id=obj.id,
        object_version=obj.version,
        inputs=payload.model_dump(),
        results=calculate(payload),
        author=identity.name,
    )
    session.add(result)
    audit(
        session,
        obj.id,
        "evaluation",
        f"Сохранён расчёт. Лимит выкупа {result.results['max_buyout_price']} ₽",
        identity.name,
    )
    session.commit()
    session.refresh(result)
    return result


@router.put("/objects/{object_id}/checks/{code}")
def save_check(
    object_id: int,
    code: str,
    payload: CheckInput,
    session: SessionDep,
    identity: Writer,
):
    obj = get_object(session, object_id, lock=True)
    check = session.exec(
        select(Check).where(Check.object_id == object_id, Check.code == code)
    ).first()
    if not check:
        raise HTTPException(404, "Проверка не найдена")
    check.status, check.evidence = payload.status, payload.evidence
    check.author, check.checked_at = identity.name, now()
    session.add(check)
    # Checks are read live by the purchase gate; a revoked check blocks buying.
    audit(
        session,
        obj.id,
        "check",
        f"{check.label}: {check.status}. {check.evidence}",
        identity.name,
    )
    session.commit()
    session.refresh(check)
    return check


@router.post("/objects/{object_id}/activities", status_code=201)
def add_note(object_id: int, payload: NoteInput, session: SessionDep, identity: Writer):
    get_object(session, object_id)
    audit(session, object_id, payload.kind, payload.body, identity.name)
    session.commit()
    return {"saved": True, "sent_externally": False}


@router.get("/tasks")
def tasks(session: SessionDep, identity: CurrentIdentity):
    return session.exec(
        select(WorkTask).order_by(WorkTask.created_at.desc()).limit(500)
    ).all()


@router.post("/tasks", status_code=201)
def create_task(payload: TaskInput, session: SessionDep, identity: Writer):
    get_object(session, payload.object_id)
    task = WorkTask(**payload.model_dump())
    session.add(task)
    audit(session, payload.object_id, "task", payload.title, identity.name)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/tasks/{task_id}")
def complete_task(
    task_id: int, payload: TaskUpdate, session: SessionDep, identity: Writer
):
    task = session.get(WorkTask, task_id)
    if not task:
        raise HTTPException(404, "Задача не найдена")
    task.completed_at = now() if payload.done else None
    session.add(task)
    audit(
        session,
        task.object_id,
        "task",
        ("Выполнено: " if payload.done else "Возвращено: ") + task.title,
        identity.name,
    )
    session.commit()
    return {"saved": True}


@router.get("/buyers")
def buyers(session: SessionDep, identity: CurrentIdentity):
    return session.exec(
        select(Buyer).order_by(Buyer.updated_at.desc()).limit(500)
    ).all()


@router.post("/buyers", status_code=201)
def add_buyer(payload: BuyerInput, session: SessionDep, identity: Writer):
    buyer = Buyer(**payload.model_dump())
    session.add(buyer)
    audit(session, None, "buyer", "Добавлена заявка покупателя", identity.name)
    session.commit()
    session.refresh(buyer)
    return buyer


@router.put("/buyers/{buyer_id}")
def edit_buyer(
    buyer_id: int, payload: BuyerInput, session: SessionDep, identity: Writer
):
    buyer = session.get(Buyer, buyer_id)
    if not buyer:
        raise HTTPException(404, "Заявка не найдена")
    buyer.sqlmodel_update(payload.model_dump())
    buyer.updated_at = now()
    session.add(buyer)
    session.commit()
    session.refresh(buyer)
    return buyer


@router.get("/searches")
def searches(session: SessionDep, identity: CurrentIdentity):
    return session.exec(select(Search).order_by(Search.id.desc())).all()


@router.post("/searches", status_code=201)
def save_search(payload: SearchInput, session: SessionDep, identity: Writer):
    search = Search(name=payload.name, filters=payload.filters.model_dump())
    session.add(search)
    session.commit()
    session.refresh(search)
    return search


@router.get("/overview")
def overview(session: SessionDep, identity: CurrentIdentity):
    stages = dict(
        session.exec(select(Object.stage, func.count()).group_by(Object.stage)).all()
    )
    urgent = session.exec(
        select(func.count())
        .select_from(Object)
        .where(Object.urgency_evidence != "", Object.stage.notin_(["rejected", "sold"]))
    ).one()
    overdue = session.exec(
        select(func.count())
        .select_from(WorkTask)
        .where(WorkTask.completed_at.is_(None), WorkTask.due_at < now())
    ).one()
    pending_checks = session.exec(
        select(func.count()).select_from(Check).where(Check.status == "unknown")
    ).one()
    # Asking-price exposure is labelled as such, never claimed as money invested.
    asking_exposure = session.exec(
        select(func.coalesce(func.sum(Object.asking_price), 0)).where(
            Object.stage.in_(["bought", "selling"])
        )
    ).one()
    return {
        "total": sum(stages.values()),
        "stages": stages,
        "urgent": urgent,
        "overdue_tasks": overdue,
        "pending_checks": pending_checks,
        "portfolio_asking_exposure": asking_exposure,
        "recent_activity": session.exec(
            select(Activity).order_by(Activity.id.desc()).limit(25)
        ).all(),
        "as_of": datetime.utcnow(),
    }


@router.get("/sources")
def sources(session: SessionDep, identity: CurrentIdentity):
    counts = dict(
        session.exec(
            select(SourceListing.source, func.count()).group_by(SourceListing.source)
        ).all()
    )
    return {
        "sources": [
            {"id": key, "name": name, "status": status, "count": counts.get(key, 0)}
            for key, name, status in [
                ("manual", "Ручное добавление", "available"),
                ("file", "Импорт JSON / CSV", "available"),
                ("avito", "Авито", "not_connected"),
                ("cian", "ЦИАН", "not_connected"),
                ("domclick", "Домклик", "not_connected"),
                ("torgi", "Торги", "not_connected"),
                ("partners", "Партнёрский поток", "not_connected"),
            ]
        ],
        "runs": session.exec(
            select(ImportRun).order_by(ImportRun.id.desc()).limit(30)
        ).all(),
    }
