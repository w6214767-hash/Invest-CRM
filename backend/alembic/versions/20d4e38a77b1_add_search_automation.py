"""Добавляет профили поиска и журнал запусков автоматизации."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20d4e38a77b1"
down_revision: Union[str, Sequence[str], None] = "80f829df3cf9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("search_profiles", sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("districts", sa.JSON(), nullable=False), sa.Column("min_price", sa.Integer(), nullable=False), sa.Column("max_price", sa.Integer(), nullable=False), sa.Column("min_area", sa.Float(), nullable=False), sa.Column("max_area", sa.Float(), nullable=False), sa.Column("min_discount", sa.Float(), nullable=False), sa.Column("land_use", sa.JSON(), nullable=False), sa.Column("exclude_words", sa.JSON(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False))
    op.create_table("integration_runs", sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.Column("id", sa.Integer(), primary_key=True), sa.Column("profile_id", sa.Integer(), sa.ForeignKey("search_profiles.id")), sa.Column("status", sa.String(50), nullable=False), sa.Column("imported_count", sa.Integer(), nullable=False), sa.Column("qualified_count", sa.Integer(), nullable=False), sa.Column("duplicates_count", sa.Integer(), nullable=False), sa.Column("review_count", sa.Integer(), nullable=False), sa.Column("actor", sa.String(100), nullable=False), sa.Column("details", sa.JSON(), nullable=False))


def downgrade() -> None:
    op.drop_table("integration_runs")
    op.drop_table("search_profiles")
