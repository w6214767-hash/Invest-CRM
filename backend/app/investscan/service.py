"""Durable import, price history, comparable evidence and conservative stage gates."""

import secrets
from datetime import timedelta
from statistics import median

from fastapi import HTTPException
from sqlalchemy import update
from sqlmodel import select

from app.investscan.schemas import ObjectInput
from app.models.investscan import (
    Activity,
    Buyer,
    Check,
    Evaluation,
    Object,
    PriceObservation,
    SourceListing,
    now,
)

CHECKS = [
    ("ownership", "Право собственности и полномочия продавца"),
    ("encumbrance", "Обременения и ограничения"),
    ("documents", "Документы и характеристики объекта"),
    ("condition", "Осмотр и бюджет подготовки"),
    ("exit", "Спрос и подтверждение цены продажи"),
]
LAND_CHECKS = [
    ("land_use", "ВРИ, границы и возможность использования"),
    ("access", "Подъезд и коммуникации"),
]
TRANSITIONS = {
    "new": {"review", "rejected"},
    "review": {"negotiation", "approval", "rejected"},
    "negotiation": {"review", "approval", "rejected"},
    "approval": {"review", "bought", "rejected"},
    "bought": {"selling"},
    "selling": {"sold"},
    "sold": set(),
    "rejected": {"review"},
}


def get_object(session, object_id, lock=False):
    query = select(Object).where(Object.id == object_id)
    if lock:
        query = query.with_for_update()
    obj = session.exec(query).first()
    if not obj:
        raise HTTPException(404, "Объект не найден")
    return obj


def audit(session, object_id, kind, body, author):
    session.add(Activity(object_id=object_id, kind=kind, body=body, author=author))


def bump(session, obj, version, values):
    result = session.exec(
        update(Object)
        .where(Object.id == obj.id, Object.version == version)
        .values(**values, version=version + 1, updated_at=now())
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        raise HTTPException(
            409, "Объект уже изменён. Обновите карточку перед сохранением"
        )
    session.expire(obj)
    session.refresh(obj)


def ingest(session, payload: ObjectInput, author):
    external_id = payload.external_id or secrets.token_hex(16)
    source = session.exec(
        select(SourceListing)
        .where(
            SourceListing.source == payload.source,
            SourceListing.external_id == external_id,
        )
        .with_for_update()
    ).first()
    values = payload.model_dump(exclude={"source", "external_id", "url"})
    if source:
        obj = get_object(session, source.object_id, lock=True)
        changed = source.price != payload.asking_price
        source.last_seen = now()
        source.url = payload.url or source.url
        if changed:
            source.price = payload.asking_price
            session.add(
                PriceObservation(
                    object_id=obj.id, listing_id=source.id, price=payload.asking_price
                )
            )
            bump(session, obj, obj.version, {"asking_price": payload.asking_price})
            audit(
                session,
                obj.id,
                "price",
                f"Источник {payload.source}: цена {payload.asking_price} ₽",
                author,
            )
        session.add(source)
        session.flush()
        return obj, "updated" if changed else "unchanged"
    # Cross-source/cadastral similarities are suggestions, never silent merges.
    obj = Object(**values)
    session.add(obj)
    session.flush()
    source = SourceListing(
        object_id=obj.id,
        source=payload.source,
        external_id=external_id,
        url=payload.url,
        price=payload.asking_price,
    )
    session.add(source)
    session.flush()
    session.add(
        PriceObservation(
            object_id=obj.id, listing_id=source.id, price=payload.asking_price
        )
    )
    checks = CHECKS + (LAND_CHECKS if obj.asset_type in {"land", "house"} else [])
    for code, label in checks:
        session.add(Check(object_id=obj.id, code=code, label=label))
    audit(session, obj.id, "created", f"Объект добавлен из {payload.source}", author)
    session.flush()
    return obj, "created"


def latest_evaluation(session, object_id):
    return session.exec(
        select(Evaluation)
        .where(Evaluation.object_id == object_id)
        .order_by(Evaluation.id.desc())
    ).first()


def comparable_market(session, obj):
    if not obj.district:
        return {
            "count": 0,
            "estimated_price": None,
            "confidence": "insufficient",
            "items": [],
            "basis": "Укажите район для подбора аналогов",
        }
    query = select(Object).where(
        Object.id != obj.id,
        Object.asset_type == obj.asset_type,
        Object.district == obj.district,
        Object.area >= obj.area * 0.7,
        Object.area <= obj.area * 1.3,
        Object.id.in_(
            select(SourceListing.object_id).where(
                SourceListing.last_seen >= now() - timedelta(days=90)
            )
        ),
        Object.stage.notin_(["rejected", "sold"]),
    )
    if obj.asset_type == "land":
        if not obj.land_use:
            return {
                "count": 0,
                "estimated_price": None,
                "confidence": "insufficient",
                "items": [],
                "basis": "Для земли нужен ВРИ",
            }
        query = query.where(Object.land_use == obj.land_use)
    if obj.cadastral_number:
        query = query.where(
            (Object.cadastral_number != obj.cadastral_number)
            | (Object.cadastral_number.is_(None))
        )
    candidates = list(
        session.exec(query.order_by(Object.updated_at.desc()).limit(100)).all()
    )
    # Identical cadastral numbers count as one comparable, including reposts.
    seen = set()
    items = []
    for item in candidates:
        key = item.cadastral_number or f"id:{item.id}"
        if key not in seen:
            seen.add(key)
            items.append(item)
    estimated = (
        round(median(x.asking_price / x.area for x in items) * obj.area)
        if len(items) >= 3
        else None
    )
    return {
        "count": len(items),
        "estimated_price": estimated,
        "confidence": "preliminary" if estimated else "insufficient",
        "items": [
            {"id": x.id, "title": x.title, "price": x.asking_price, "area": x.area}
            for x in items
        ],
        "basis": "Медиана цен предложений в базе: тот же тип, район, площадь ±30%, обновление до 90 дней. Это не цены состоявшихся сделок и не независимая оценка.",
    }


def match_buyers(session, obj):
    buyers = session.exec(
        select(Buyer).where(
            Buyer.active,
            Buyer.asset_type == obj.asset_type,
            Buyer.max_budget >= obj.asking_price,
            Buyer.updated_at >= now() - timedelta(days=30),
        )
    ).all()
    return [
        b
        for b in buyers
        if (
            not b.districts
            or obj.district.casefold() in [x.casefold() for x in b.districts]
        )
        and b.min_area <= obj.area
        and (b.max_area is None or b.max_area >= obj.area)
    ]


def stage_gate(session, obj, target, identity):
    if target not in TRANSITIONS[obj.stage]:
        raise HTTPException(409, "Такой переход между этапами недоступен")
    if target in {"bought", "sold"} and identity.role != "owner":
        raise HTTPException(403, "Фиксация покупки и продажи доступна собственнику")
    if target in {"approval", "bought"}:
        checks = list(
            session.exec(select(Check).where(Check.object_id == obj.id)).all()
        )
        if not checks or any(c.status != "passed" for c in checks):
            raise HTTPException(409, "Сначала завершите все проверки с подтверждением")
        evaluation = latest_evaluation(session, obj.id)
        if not evaluation or evaluation.object_version != obj.version:
            raise HTTPException(409, "Нужен расчёт для текущей версии объекта")
        if evaluation.results["headroom"] < 0:
            raise HTTPException(409, "Цена покупки выше рассчитанного лимита")
