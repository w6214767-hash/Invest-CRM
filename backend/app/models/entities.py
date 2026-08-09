"""SQLModel-модели предметной области инвестиционной CRM."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class ListingStatus(str, Enum):
    """Статус обработки объявления."""

    NEW = "new"
    SCORED = "scored"
    IN_NEGOTIATION = "in_negotiation"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class NegotiationStage(str, Enum):
    """Этап полуавтоматических переговоров с продавцом."""

    NEW = "new"
    NEED_FIRST_CONTACT = "need_first_contact"
    WAITING_REPLY = "waiting_reply"
    QUALIFIED = "qualified"
    BARGAIN_STARTED = "bargain_started"
    HUMAN_REVIEW = "human_review"
    OFFER_READY = "offer_ready"
    ARCHIVED = "archived"


class SellerType(str, Enum):
    """Тип продавца по данным объявления и диалога."""

    OWNER = "owner"
    AGENT = "agent"
    DEVELOPER = "developer"
    UNKNOWN = "unknown"


class DealStage(str, Enum):
    """Этап сделки в инвестиционной воронке."""

    LEAD = "lead"
    QUALIFICATION = "qualification"
    DUE_DILIGENCE = "due_diligence"
    OFFER = "offer"
    CONTRACT = "contract"
    WON = "won"
    LOST = "lost"


class TimestampedModel(SQLModel):
    """Общие временные поля сущностей."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class User(TimestampedModel, table=True):
    """Пользователь CRM: менеджер, аналитик или администратор."""

    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    full_name: str = Field(max_length=255)
    password_hash: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class Seller(TimestampedModel, table=True):
    """Продавец участка, объединённый по контактам Авито."""

    __tablename__ = "sellers"
    id: Optional[int] = Field(default=None, primary_key=True)
    avito_user_id: Optional[str] = Field(default=None, index=True, unique=True)
    name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, index=True, max_length=50)
    seller_type: SellerType = Field(default=SellerType.UNKNOWN)
    urgency_score: float = Field(default=0.0, ge=0, le=100)
    notes: Optional[str] = Field(default=None)


class Listing(TimestampedModel, table=True):
    """Объявление о продаже земельного участка."""

    __tablename__ = "listings"
    id: Optional[int] = Field(default=None, primary_key=True)
    avito_item_id: Optional[str] = Field(default=None, index=True, unique=True)
    seller_id: Optional[int] = Field(default=None, foreign_key="sellers.id", index=True)
    title: str = Field(max_length=500)
    description: str = Field(default="")
    url: Optional[str] = Field(default=None, max_length=1000)
    region: Optional[str] = Field(default=None, index=True, max_length=255)
    district: Optional[str] = Field(default=None, index=True, max_length=255)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    area_sotka: float = Field(gt=0)
    price_rub: int = Field(gt=0)
    price_per_sotka: Optional[float] = Field(default=None)
    cadastral_number: Optional[str] = Field(default=None, index=True, max_length=100)
    status: ListingStatus = Field(default=ListingStatus.NEW)
    negotiation_stage: NegotiationStage = Field(default=NegotiationStage.NEW)
    score: Optional[float] = Field(default=None, ge=0, le=100)
    discount_pct: Optional[float] = Field(default=None)
    liquidity_score: float = Field(default=50.0, ge=0, le=100)
    location_score: float = Field(default=50.0, ge=0, le=100)
    docs_score: float = Field(default=50.0, ge=0, le=100)
    utility_score: float = Field(default=50.0, ge=0, le=100)
    seller_urgency_score: float = Field(default=0.0, ge=0, le=100)
    red_flags: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    raw_payload: dict = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )


class Comp(TimestampedModel, table=True):
    """Сопоставимое объявление для расчёта рыночной цены."""

    __tablename__ = "comps"
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listings.id", index=True)
    source: str = Field(default="avito", max_length=100)
    external_id: Optional[str] = Field(default=None, index=True)
    cluster_key: str = Field(index=True, max_length=255)
    area_sotka: float = Field(gt=0)
    price_rub: int = Field(gt=0)
    price_per_sotka: float = Field(gt=0)
    is_active: bool = Field(default=True)


class Valuation(TimestampedModel, table=True):
    """Результат оценки стоимости конкретного объявления."""

    __tablename__ = "valuations"
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listings.id", index=True)
    cluster_key: str = Field(index=True, max_length=255)
    median_price_per_sotka: float = Field(gt=0)
    estimated_market_price: int = Field(gt=0)
    discount_pct: float
    score: float = Field(ge=0, le=100)
    method: str = Field(default="median_comps", max_length=100)


class Chat(TimestampedModel, table=True):
    """Диалог Авито, связанный с объявлением и продавцом."""

    __tablename__ = "chats"
    id: Optional[int] = Field(default=None, primary_key=True)
    avito_chat_id: str = Field(index=True, unique=True, max_length=255)
    listing_id: Optional[int] = Field(
        default=None, foreign_key="listings.id", index=True
    )
    seller_id: Optional[int] = Field(default=None, foreign_key="sellers.id", index=True)
    last_message_at: Optional[datetime] = Field(default=None)
    is_open: bool = Field(default=True)


class Message(TimestampedModel, table=True):
    """Входящее или исходящее сообщение в диалоге."""

    __tablename__ = "messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", index=True)
    avito_message_id: Optional[str] = Field(default=None, index=True, unique=True)
    direction: str = Field(max_length=20)
    body: str
    sent_by_human: bool = Field(default=False)
    sent_at: datetime = Field(default_factory=datetime.utcnow)


class NegotiationEvent(TimestampedModel, table=True):
    """Аудит перехода по стейт-машине переговоров."""

    __tablename__ = "negotiation_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listings.id", index=True)
    from_stage: NegotiationStage
    to_stage: NegotiationStage
    reason: str = Field(max_length=1000)
    actor: str = Field(default="system", max_length=100)
    metadata_json: dict = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )


class Offer(TimestampedModel, table=True):
    """Финансовое предложение продавцу."""

    __tablename__ = "offers"
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listings.id", index=True)
    seller_id: Optional[int] = Field(default=None, foreign_key="sellers.id", index=True)
    amount_rub: int = Field(gt=0)
    status: str = Field(default="draft", max_length=50)
    valid_until: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class Deal(TimestampedModel, table=True):
    """Сделка, переданная в Bitrix24 или ведущаяся внутри CRM."""

    __tablename__ = "deals"
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listings.id", index=True)
    seller_id: Optional[int] = Field(default=None, foreign_key="sellers.id", index=True)
    offer_id: Optional[int] = Field(default=None, foreign_key="offers.id", index=True)
    bitrix24_deal_id: Optional[str] = Field(default=None, index=True, unique=True)
    stage: DealStage = Field(default=DealStage.LEAD)
    amount_rub: Optional[int] = Field(default=None)
    manager_name: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None)


class Task(TimestampedModel, table=True):
    """Задача менеджеру по лоту или сделке."""

    __tablename__ = "tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: Optional[int] = Field(
        default=None, foreign_key="listings.id", index=True
    )
    deal_id: Optional[int] = Field(default=None, foreign_key="deals.id", index=True)
    assignee_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    due_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


class PipelineStage(TimestampedModel, table=True):
    """Настраиваемый этап локальной воронки."""

    __tablename__ = "pipeline_stages"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    order_index: int = Field(index=True)
    color: str = Field(default="#2563eb", max_length=20)
    is_terminal: bool = Field(default=False)
