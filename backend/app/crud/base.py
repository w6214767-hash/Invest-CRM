"""Типизированный базовый CRUD для SQLModel-сущностей."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Стандартные операции создания, чтения, изменения и удаления."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, session: Session, entity_id: int) -> ModelType | None:
        """Возвращает сущность по первичному ключу."""
        return session.get(self.model, entity_id)

    def get_multi(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Возвращает страницу сущностей."""
        return list(session.exec(select(self.model).offset(skip).limit(limit)).all())

    def create(
        self, session: Session, *, obj_in: CreateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Создаёт сущность и фиксирует транзакцию."""
        data = (
            obj_in.model_dump(exclude_unset=True)
            if isinstance(obj_in, BaseModel)
            else obj_in
        )
        db_obj = self.model.model_validate(data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Обновляет только переданные поля сущности."""
        data = (
            obj_in.model_dump(exclude_unset=True)
            if isinstance(obj_in, BaseModel)
            else obj_in
        )
        db_obj.sqlmodel_update(data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def remove(self, session: Session, *, entity_id: int) -> ModelType | None:
        """Удаляет сущность по идентификатору."""
        db_obj = self.get(session, entity_id)
        if db_obj is None:
            return None
        session.delete(db_obj)
        session.commit()
        return db_obj
