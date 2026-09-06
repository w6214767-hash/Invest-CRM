"""Validated API payloads. Amounts are integer RUB; no silent currency conversion."""

from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Asset = Literal["land", "apartment", "house", "commercial"]
Stage = Literal[
    "new", "review", "negotiation", "approval", "bought", "selling", "sold", "rejected"
]


class Payload(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True, allow_inf_nan=False
    )


class ObjectInput(Payload):
    title: str = Field(min_length=3, max_length=500)
    asset_type: Asset
    district: str = Field(default="", max_length=160)
    address: str = Field(default="", max_length=600)
    area: float = Field(gt=0, le=10_000_000)
    asking_price: int = Field(gt=0, le=2_000_000_000)
    land_use: str = Field(default="", max_length=120)
    cadastral_number: str | None = Field(default=None, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    description: str = Field(default="", max_length=20000)
    urgency_evidence: str = Field(default="", max_length=2000)
    seller_deadline: datetime | None = None
    source: str = Field(default="manual", pattern=r"^[a-z0-9_-]{1,60}$")
    external_id: str | None = Field(default=None, max_length=255)
    url: str = Field(default="", max_length=1500)

    @field_validator("url")
    @classmethod
    def safe_url(cls, value):
        if value and (
            urlsplit(value).scheme not in {"http", "https"}
            or not urlsplit(value).hostname
            or urlsplit(value).username
        ):
            raise ValueError("Нужна обычная ссылка http/https без пароля")
        return value

    @field_validator("cadastral_number", "external_id")
    @classmethod
    def empty_to_none(cls, value):
        return value or None

    @model_validator(mode="after")
    def coordinates_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Укажите обе координаты")
        return self


class ImportPayload(Payload):
    items: list[ObjectInput] = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def needs_ids(self):
        if any(not item.external_id for item in self.items):
            raise ValueError(
                "Для повторяемого импорта каждому объекту нужен external_id"
            )
        return self


class FinanceInput(Payload):
    object_version: int = Field(gt=0)
    resale_price: int = Field(gt=0, le=2_000_000_000)
    purchase_price: int = Field(gt=0, le=2_000_000_000)
    repairs: int = Field(default=0, ge=0, le=2_000_000_000)
    legal_costs: int = Field(default=0, ge=0, le=2_000_000_000)
    other_costs: int = Field(default=0, ge=0, le=2_000_000_000)
    reserve: int = Field(default=0, ge=0, le=2_000_000_000)
    target_profit: int = Field(default=0, ge=0, le=2_000_000_000)
    holding_months: int = Field(default=3, ge=1, le=120)
    monthly_holding: int = Field(default=0, ge=0, le=2_000_000_000)
    annual_finance_pct: float = Field(default=0, ge=0, le=100)
    financed_share_pct: float = Field(default=0, ge=0, le=100)
    sale_cost_pct: float = Field(default=0, ge=0, le=100)
    acquisition_cost_pct: float = Field(default=0, ge=0, le=100)
    resale_basis: str = Field(min_length=3, max_length=2000)


class ObjectUpdate(Payload):
    version: int = Field(gt=0)
    title: str | None = Field(default=None, min_length=3, max_length=500)
    asking_price: int | None = Field(default=None, gt=0, le=2_000_000_000)
    urgency_evidence: str | None = Field(default=None, max_length=2000)
    starred: bool | None = None
    stage: Stage | None = None
    reason: str = Field(default="", max_length=2000)


class CheckInput(Payload):
    status: Literal["unknown", "passed", "failed"]
    evidence: str = Field(default="", max_length=4000)

    @model_validator(mode="after")
    def evidence_required(self):
        if self.status != "unknown" and len(self.evidence) < 3:
            raise ValueError("Укажите документ или основание проверки")
        return self


class NoteInput(Payload):
    body: str = Field(min_length=1, max_length=10000)
    kind: Literal["note", "call", "viewing", "draft"] = "note"


class TaskInput(Payload):
    object_id: int = Field(gt=0)
    title: str = Field(min_length=3, max_length=300)
    assignee: str = Field(default="", max_length=160)
    due_at: datetime | None = None


class TaskUpdate(Payload):
    done: bool


class BuyerInput(Payload):
    name: str = Field(min_length=2, max_length=200)
    contact: str = Field(default="", max_length=300)
    asset_type: Asset
    districts: list[str] = Field(default_factory=list, max_length=50)
    max_budget: int = Field(gt=0, le=2_000_000_000)
    min_area: float = Field(default=0, ge=0)
    max_area: float | None = Field(default=None, gt=0)
    notes: str = Field(default="", max_length=4000)
    active: bool = True

    @model_validator(mode="after")
    def area_range(self):
        if self.max_area is not None and self.max_area < self.min_area:
            raise ValueError("Максимальная площадь меньше минимальной")
        return self


class FilterInput(Payload):
    q: str = Field(default="", max_length=300)
    asset_type: Asset | None = None
    district: str = Field(default="", max_length=160)
    stage: Stage | None = None
    min_price: int = Field(default=0, ge=0)
    max_price: int | None = Field(default=None, gt=0)
    min_area: float = Field(default=0, ge=0)
    max_area: float | None = Field(default=None, gt=0)
    urgent: bool = False
    starred: bool = False
    exclude: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def ranges(self):
        if self.max_price is not None and self.max_price < self.min_price:
            raise ValueError("Неверный диапазон цены")
        if self.max_area is not None and self.max_area < self.min_area:
            raise ValueError("Неверный диапазон площади")
        return self


class SearchInput(Payload):
    name: str = Field(min_length=2, max_length=200)
    filters: FilterInput
