"""Добавляет статус прочтения сообщений.

Идентификатор ревизии: 80f829df3cf9
Предыдущая ревизия: 3a8b54407db6
Дата создания: 2026-08-09 14:14:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "80f829df3cf9"
down_revision: Union[str, Sequence[str], None] = "3a8b54407db6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляет флаг прочтения с безопасным значением для старых записей."""
    # SQLite применяет DDL нетранзакционно. Если старая версия
    # миграции упала после ADD COLUMN, колонка уже осталась в базе.
    # Проверка делает повторный `alembic upgrade head` безопасным.
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("messages")}
    if "is_read" not in columns:
        op.add_column(
            "messages",
            sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    # SQLite не поддерживает `ALTER COLUMN ... DROP DEFAULT`.
    # Batch-режим пересоздаёт таблицу для SQLite и остаётся обычным
    # ALTER TABLE для PostgreSQL.
    with op.batch_alter_table("messages") as batch_op:
        batch_op.alter_column("is_read", server_default=None)


def downgrade() -> None:
    """Удаляет флаг прочтения сообщений."""
    op.drop_column("messages", "is_read")
