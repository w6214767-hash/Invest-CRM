"""Independent investment workspace; legacy CRM tables remain intact."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel


def now() -> datetime:
    return datetime.utcnow()


class Object(SQLModel, table=True):
    __tablename__ = "is_objects"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    asset_type: str = Field(index=True, max_length=30)
    district: str = Field(default="", index=True, max_length=160)
    address: str = Field(default="", max_length=600)
    area: float = Field(gt=0)
    land_use: str = Field(default="", max_length=120)
    cadastral_number: Optional[str] = Field(default=None, index=True, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asking_price: int = Field(gt=0)
    description: str = ""
    urgency_evidence: str = ""
    seller_deadline: Optional[datetime] = None
    stage: str = Field(default="new", index=True, max_length=30)
    starred: bool = False
    version: int = 1
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class SourceListing(SQLModel, table=True):
    __tablename__ = "is_source_listings"
    __table_args__ = (UniqueConstraint("source", "external_id"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: int = Field(foreign_key="is_objects.id", index=True)
    source: str = Field(max_length=60)
    external_id: str = Field(max_length=255)
    url: str = Field(default="", max_length=1500)
    price: int
    first_seen: datetime = Field(default_factory=now)
    last_seen: datetime = Field(default_factory=now)


class PriceObservation(SQLModel, table=True):
    __tablename__ = "is_prices"
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: int = Field(foreign_key="is_objects.id", index=True)
    listing_id: Optional[int] = Field(default=None, foreign_key="is_source_listings.id")
    price: int
    observed_at: datetime = Field(default_factory=now)


class Evaluation(SQLModel, table=True):
    __tablename__ = "is_evaluations"
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: int = Field(foreign_key="is_objects.id", index=True)
    object_version: int
    inputs: dict = Field(sa_column=Column(JSON, nullable=False))
    results: dict = Field(sa_column=Column(JSON, nullable=False))
    author: str
    created_at: datetime = Field(default_factory=now)


class Check(SQLModel, table=True):
    __tablename__ = "is_checks"
    __table_args__ = (UniqueConstraint("object_id", "code"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: int = Field(foreign_key="is_objects.id", index=True)
    code: str = Field(max_length=60)
    label: str = Field(max_length=200)
    status: str = Field(default="unknown", max_length=20)
    evidence: str = ""
    author: str = ""
    checked_at: Optional[datetime] = None


class Activity(SQLModel, table=True):
    __tablename__ = "is_activity"
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: Optional[int] = Field(
        default=None, foreign_key="is_objects.id", index=True
    )
    kind: str = Field(max_length=60)
    body: str
    author: str
    created_at: datetime = Field(default_factory=now)


class WorkTask(SQLModel, table=True):
    __tablename__ = "is_tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: int = Field(foreign_key="is_objects.id", index=True)
    title: str = Field(max_length=300)
    assignee: str = Field(default="", max_length=160)
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=now)


class Buyer(SQLModel, table=True):
    __tablename__ = "is_buyers"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    contact: str = Field(default="", max_length=300)
    asset_type: str = Field(max_length=30)
    districts: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    max_budget: int
    min_area: float = 0
    max_area: Optional[float] = None
    notes: str = ""
    active: bool = True
    updated_at: datetime = Field(default_factory=now)


class Search(SQLModel, table=True):
    __tablename__ = "is_searches"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    filters: dict = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=now)


class ImportRun(SQLModel, table=True):
    __tablename__ = "is_import_runs"
    id: Optional[int] = Field(default=None, primary_key=True)
    author: str
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    created_at: datetime = Field(default_factory=now)


class Identity(SQLModel, table=True):
    __tablename__ = "is_identities"
    __table_args__ = (UniqueConstraint("issuer", "subject"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    issuer: str = Field(max_length=500)
    subject: str = Field(max_length=255)
    name: str = Field(max_length=255)
    role: str = Field(max_length=30)
    active: bool = True


class LoginSession(SQLModel, table=True):
    __tablename__ = "is_sessions"
    token_hash: str = Field(primary_key=True, max_length=64)
    identity_id: int = Field(foreign_key="is_identities.id", index=True)
    csrf_token: str = Field(max_length=100)
    expires_at: datetime
    created_at: datetime = Field(default_factory=now)
