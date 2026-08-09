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
    op.add_column(
        "messages",
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("messages", "is_read", server_default=None)


def downgrade() -> None:
    """Удаляет флаг прочтения сообщений."""
    op.drop_column("messages", "is_read")
