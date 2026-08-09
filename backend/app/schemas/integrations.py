"""Схемы центра поиска и интеграций."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchProfilePayload(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    districts: list[str] = Field(default_factory=list)
    min_price: int = Field(ge=0)
    max_price: int = Field(gt=0)
    min_area: float = Field(gt=0)
    max_area: float = Field(gt=0)
    min_discount: float = Field(ge=0, le=100)
    land_use: list[str] = Field(default_factory=list)
    exclude_words: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.min_price > self.max_price or self.min_area > self.max_area:
            raise ValueError("Минимальное значение не может быть больше максимального")
        return self


class SearchProfileRead(SearchProfilePayload):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool


class IntegrationSourceRead(BaseModel):
    id: str
    name: str
    status: str
    configured: bool


class ReviewListingRead(BaseModel):
    id: int
    title: str
    score: float | None
    red_flags: list[str]


class AgentAuditRead(BaseModel):
    id: int
    created_at: datetime
    actor: str
    action: str
    details: dict


class IntegrationOverview(BaseModel):
    sources: list[IntegrationSourceRead]
    profile: SearchProfileRead
    review_queue: list[ReviewListingRead]
    audit: list[AgentAuditRead]
    metrics: dict[str, int | float]


class RunResult(BaseModel):
    run_id: int
    imported_count: int
    qualified_count: int
    duplicates_count: int
    review_count: int
