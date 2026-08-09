"""Pydantic-схемы для входных и выходных данных REST API."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import DealStage, ListingStatus, NegotiationStage, SellerType


class ORMModel(BaseModel):
    """Базовая схема, способная читать данные из ORM-моделей."""

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Регистрация пользователя CRM."""

    email: str
    full_name: str
    password: str = Field(min_length=8)


class UserRead(ORMModel):
    """Безопасное представление пользователя."""

    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool


class Token(BaseModel):
    """Ответ успешной аутентификации."""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Данные входа без зависимости от form-data."""

    email: str
    password: str


class SellerCreate(BaseModel):
    """Создание карточки продавца."""

    avito_user_id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    seller_type: SellerType = SellerType.UNKNOWN
    urgency_score: float = Field(default=0, ge=0, le=100)
    notes: Optional[str] = None


class SellerUpdate(BaseModel):
    """Частичное обновление карточки продавца."""

    name: Optional[str] = None
    phone: Optional[str] = None
    seller_type: Optional[SellerType] = None
    urgency_score: Optional[float] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = None


class SellerRead(ORMModel):
    """Карточка продавца в API."""

    id: int
    avito_user_id: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    seller_type: SellerType
    urgency_score: float
    notes: Optional[str]
    created_at: datetime


class ListingCreate(BaseModel):
    """Создание объявления вручную либо из интеграции."""

    avito_item_id: Optional[str] = None
    seller_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    url: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_sotka: float = Field(gt=0)
    price_rub: int = Field(gt=0)
    cadastral_number: Optional[str] = None
    liquidity_score: float = Field(default=50, ge=0, le=100)
    location_score: float = Field(default=50, ge=0, le=100)
    docs_score: float = Field(default=50, ge=0, le=100)
    utility_score: float = Field(default=50, ge=0, le=100)


class ListingUpdate(BaseModel):
    """Частичное обновление объявления."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    price_rub: Optional[int] = Field(default=None, gt=0)
    area_sotka: Optional[float] = Field(default=None, gt=0)
    status: Optional[ListingStatus] = None
    negotiation_stage: Optional[NegotiationStage] = None
    cadastral_number: Optional[str] = None
    liquidity_score: Optional[float] = Field(default=None, ge=0, le=100)
    location_score: Optional[float] = Field(default=None, ge=0, le=100)
    docs_score: Optional[float] = Field(default=None, ge=0, le=100)
    utility_score: Optional[float] = Field(default=None, ge=0, le=100)


class ListingRead(ORMModel):
    """Полное представление объявления."""

    id: int
    avito_item_id: Optional[str]
    seller_id: Optional[int]
    title: str
    description: str
    url: Optional[str]
    region: Optional[str]
    district: Optional[str]
    area_sotka: float
    price_rub: int
    price_per_sotka: Optional[float]
    cadastral_number: Optional[str]
    status: ListingStatus
    negotiation_stage: NegotiationStage
    score: Optional[float]
    discount_pct: Optional[float]
    red_flags: list[str]
    created_at: datetime


class OfferCreate(BaseModel):
    """Черновик или отправленное предложение."""

    listing_id: int
    seller_id: Optional[int] = None
    amount_rub: int = Field(gt=0)
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class OfferUpdate(BaseModel):
    """Изменение предложения."""

    amount_rub: Optional[int] = Field(default=None, gt=0)
    status: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class OfferRead(ORMModel):
    """Предложение в API."""

    id: int
    listing_id: int
    seller_id: Optional[int]
    amount_rub: int
    status: str
    valid_until: Optional[datetime]
    notes: Optional[str]
    created_at: datetime


class DealCreate(BaseModel):
    """Создание инвестиционной сделки."""

    listing_id: int
    seller_id: Optional[int] = None
    offer_id: Optional[int] = None
    amount_rub: Optional[int] = Field(default=None, gt=0)
    manager_name: Optional[str] = None
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    """Изменение стадии или параметров сделки."""

    stage: Optional[DealStage] = None
    amount_rub: Optional[int] = Field(default=None, gt=0)
    manager_name: Optional[str] = None
    notes: Optional[str] = None
    bitrix24_deal_id: Optional[str] = None


class DealRead(ORMModel):
    """Сделка в API."""

    id: int
    listing_id: int
    seller_id: Optional[int]
    offer_id: Optional[int]
    bitrix24_deal_id: Optional[str]
    stage: DealStage
    amount_rub: Optional[int]
    manager_name: Optional[str]
    notes: Optional[str]
    created_at: datetime


class NegotiationAction(BaseModel):
    """Действие над состоянием переговоров."""

    action: str
    message_text: str = ""
    mode: str = "assisted"
    actor: str = "manager"


class NegotiationResult(BaseModel):
    """Результат обработки события переговоров."""

    stage: NegotiationStage
    escalated: bool
    escalation_reasons: list[str]
    draft_message: Optional[str] = None


class NegotiationMessagePreview(BaseModel):
    """Последнее сообщение, выводимое в строке списка переговоров."""

    body: str
    sent_at: datetime


class NegotiationListItem(BaseModel):
    """Краткое представление активного диалога с продавцом."""

    listing_id: int
    title: str
    district: Optional[str] = None
    price_rub: int
    discount_pct: Optional[float] = None
    score: Optional[float] = None
    stage: NegotiationStage
    seller_name: Optional[str] = None
    last_message: Optional[NegotiationMessagePreview] = None
    unread_count: int = 0
    escalated: bool = False


class NegotiationListingSummary(BaseModel):
    """Короткая карточка участка в шапке диалога."""

    id: int
    title: str
    district: Optional[str] = None
    price_rub: int
    discount_pct: Optional[float] = None
    score: Optional[float] = None


class NegotiationSellerSummary(BaseModel):
    """Данные продавца, необходимые менеджеру в диалоге."""

    name: Optional[str] = None
    seller_type: SellerType = SellerType.UNKNOWN
    urgency_score: float = 0


class NegotiationMessageRead(BaseModel):
    """Сообщение в ленте переговоров."""

    id: int
    direction: str
    body: str
    sent_at: datetime
    sent_by_human: bool


class NegotiationEventRead(BaseModel):
    """Запись аудита перехода между стадиями переговоров."""

    id: int
    from_stage: NegotiationStage
    to_stage: NegotiationStage
    reason: str
    actor: str
    escalation_reasons: list[str] = Field(default_factory=list)
    created_at: datetime


class NegotiationDetail(BaseModel):
    """Полный набор данных для страницы переговоров."""

    listing: NegotiationListingSummary
    seller: NegotiationSellerSummary
    messages: list[NegotiationMessageRead] = Field(default_factory=list)
    events: list[NegotiationEventRead] = Field(default_factory=list)
    stage: NegotiationStage
    allowed_next_actions: list[NegotiationStage] = Field(default_factory=list)
    escalated: bool = False
    escalation_reasons: list[str] = Field(default_factory=list)


class NegotiationDraftRequest(BaseModel):
    """Необязательный сценарий для подготовки следующего сообщения."""

    intent: Optional[
        Literal["first_contact", "facts", "motivation", "bargain_test"]
    ] = None


class NegotiationDraftResponse(BaseModel):
    """Черновик сообщения и текст инструкции, по которой он получен."""

    draft_message: str
    prompt_used: str


class NegotiationMessageCreate(BaseModel):
    """Исходящее сообщение менеджера."""

    body: str = Field(min_length=1, max_length=10_000)


class DashboardMetrics(BaseModel):
    """Ключевые метрики рабочего стола."""

    leads_count: int
    conversion_pct: float
    average_discount_pct: float
    active_deals_count: int
