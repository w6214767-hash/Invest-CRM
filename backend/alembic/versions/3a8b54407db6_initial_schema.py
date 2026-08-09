"""Начальная схема данных

Идентификатор ревизии: 3a8b54407db6
Предыдущая ревизия:
Дата создания: 2026-08-09 10:48:42.738987
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "3a8b54407db6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Применяет изменения схемы."""
    # Команды сгенерированы Alembic; проверьте их перед применением.
    op.create_table(
        "pipeline_stages",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("color", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("is_terminal", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_pipeline_stages_order_index"),
        "pipeline_stages",
        ["order_index"],
        unique=False,
    )
    op.create_table(
        "sellers",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("avito_user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("phone", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column(
            "seller_type",
            sa.Enum("OWNER", "AGENT", "DEVELOPER", "UNKNOWN", name="sellertype"),
            nullable=False,
        ),
        sa.Column("urgency_score", sa.Float(), nullable=False),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sellers_avito_user_id"), "sellers", ["avito_user_id"], unique=True
    )
    op.create_index(op.f("ix_sellers_phone"), "sellers", ["phone"], unique=False)
    op.create_table(
        "users",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "full_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("password_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_table(
        "listings",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("avito_item_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("seller_id", sa.Integer(), nullable=True),
        sa.Column(
            "title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False
        ),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column(
            "region", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column(
            "district", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("area_sotka", sa.Float(), nullable=False),
        sa.Column("price_rub", sa.Integer(), nullable=False),
        sa.Column("price_per_sotka", sa.Float(), nullable=True),
        sa.Column(
            "cadastral_number",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "NEW",
                "SCORED",
                "IN_NEGOTIATION",
                "ARCHIVED",
                "REJECTED",
                name="listingstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "negotiation_stage",
            sa.Enum(
                "NEW",
                "NEED_FIRST_CONTACT",
                "WAITING_REPLY",
                "QUALIFIED",
                "BARGAIN_STARTED",
                "HUMAN_REVIEW",
                "OFFER_READY",
                "ARCHIVED",
                name="negotiationstage",
            ),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("discount_pct", sa.Float(), nullable=True),
        sa.Column("liquidity_score", sa.Float(), nullable=False),
        sa.Column("location_score", sa.Float(), nullable=False),
        sa.Column("docs_score", sa.Float(), nullable=False),
        sa.Column("utility_score", sa.Float(), nullable=False),
        sa.Column("seller_urgency_score", sa.Float(), nullable=False),
        sa.Column("red_flags", sa.JSON(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_listings_avito_item_id"), "listings", ["avito_item_id"], unique=True
    )
    op.create_index(
        op.f("ix_listings_cadastral_number"),
        "listings",
        ["cadastral_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_listings_district"), "listings", ["district"], unique=False
    )
    op.create_index(op.f("ix_listings_region"), "listings", ["region"], unique=False)
    op.create_index(
        op.f("ix_listings_seller_id"), "listings", ["seller_id"], unique=False
    )
    op.create_table(
        "chats",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "avito_chat_id",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column("listing_id", sa.Integer(), nullable=True),
        sa.Column("seller_id", sa.Integer(), nullable=True),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("is_open", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chats_avito_chat_id"), "chats", ["avito_chat_id"], unique=True
    )
    op.create_index(op.f("ix_chats_listing_id"), "chats", ["listing_id"], unique=False)
    op.create_index(op.f("ix_chats_seller_id"), "chats", ["seller_id"], unique=False)
    op.create_table(
        "comps",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column(
            "source", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.Column("external_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "cluster_key", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("area_sotka", sa.Float(), nullable=False),
        sa.Column("price_rub", sa.Integer(), nullable=False),
        sa.Column("price_per_sotka", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_comps_cluster_key"), "comps", ["cluster_key"], unique=False
    )
    op.create_index(
        op.f("ix_comps_external_id"), "comps", ["external_id"], unique=False
    )
    op.create_index(op.f("ix_comps_listing_id"), "comps", ["listing_id"], unique=False)
    op.create_table(
        "negotiation_events",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column(
            "from_stage",
            sa.Enum(
                "NEW",
                "NEED_FIRST_CONTACT",
                "WAITING_REPLY",
                "QUALIFIED",
                "BARGAIN_STARTED",
                "HUMAN_REVIEW",
                "OFFER_READY",
                "ARCHIVED",
                name="negotiationstage",
            ),
            nullable=False,
        ),
        sa.Column(
            "to_stage",
            sa.Enum(
                "NEW",
                "NEED_FIRST_CONTACT",
                "WAITING_REPLY",
                "QUALIFIED",
                "BARGAIN_STARTED",
                "HUMAN_REVIEW",
                "OFFER_READY",
                "ARCHIVED",
                name="negotiationstage",
            ),
            nullable=False,
        ),
        sa.Column(
            "reason", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=False
        ),
        sa.Column(
            "actor", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_negotiation_events_listing_id"),
        "negotiation_events",
        ["listing_id"],
        unique=False,
    )
    op.create_table(
        "offers",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=True),
        sa.Column("amount_rub", sa.Integer(), nullable=False),
        sa.Column(
            "status", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False
        ),
        sa.Column("valid_until", sa.DateTime(), nullable=True),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_offers_listing_id"), "offers", ["listing_id"], unique=False
    )
    op.create_index(op.f("ix_offers_seller_id"), "offers", ["seller_id"], unique=False)
    op.create_table(
        "valuations",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column(
            "cluster_key", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("median_price_per_sotka", sa.Float(), nullable=False),
        sa.Column("estimated_market_price", sa.Integer(), nullable=False),
        sa.Column("discount_pct", sa.Float(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column(
            "method", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_valuations_cluster_key"), "valuations", ["cluster_key"], unique=False
    )
    op.create_index(
        op.f("ix_valuations_listing_id"), "valuations", ["listing_id"], unique=False
    )
    op.create_table(
        "deals",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=True),
        sa.Column("offer_id", sa.Integer(), nullable=True),
        sa.Column(
            "bitrix24_deal_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "stage",
            sa.Enum(
                "LEAD",
                "QUALIFICATION",
                "DUE_DILIGENCE",
                "OFFER",
                "CONTRACT",
                "WON",
                "LOST",
                name="dealstage",
            ),
            nullable=False,
        ),
        sa.Column("amount_rub", sa.Integer(), nullable=True),
        sa.Column(
            "manager_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_deals_bitrix24_deal_id"), "deals", ["bitrix24_deal_id"], unique=True
    )
    op.create_index(op.f("ix_deals_listing_id"), "deals", ["listing_id"], unique=False)
    op.create_index(op.f("ix_deals_offer_id"), "deals", ["offer_id"], unique=False)
    op.create_index(op.f("ix_deals_seller_id"), "deals", ["seller_id"], unique=False)
    op.create_table(
        "messages",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column(
            "avito_message_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "direction", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False
        ),
        sa.Column("body", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("sent_by_human", sa.Boolean(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            ["chats.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_messages_avito_message_id"),
        "messages",
        ["avito_message_id"],
        unique=True,
    )
    op.create_index(op.f("ix_messages_chat_id"), "messages", ["chat_id"], unique=False)
    op.create_table(
        "tasks",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=True),
        sa.Column("deal_id", sa.Integer(), nullable=True),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column(
            "title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False
        ),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignee_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deal_id"],
            ["deals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tasks_assignee_id"), "tasks", ["assignee_id"], unique=False
    )
    op.create_index(op.f("ix_tasks_deal_id"), "tasks", ["deal_id"], unique=False)
    op.create_index(op.f("ix_tasks_listing_id"), "tasks", ["listing_id"], unique=False)
    # Конец сгенерированного блока.


def downgrade() -> None:
    """Откатывает изменения схемы."""
    # Команды сгенерированы Alembic; проверьте их перед применением.
    op.drop_index(op.f("ix_tasks_listing_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_deal_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_assignee_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_messages_chat_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_avito_message_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_deals_seller_id"), table_name="deals")
    op.drop_index(op.f("ix_deals_offer_id"), table_name="deals")
    op.drop_index(op.f("ix_deals_listing_id"), table_name="deals")
    op.drop_index(op.f("ix_deals_bitrix24_deal_id"), table_name="deals")
    op.drop_table("deals")
    op.drop_index(op.f("ix_valuations_listing_id"), table_name="valuations")
    op.drop_index(op.f("ix_valuations_cluster_key"), table_name="valuations")
    op.drop_table("valuations")
    op.drop_index(op.f("ix_offers_seller_id"), table_name="offers")
    op.drop_index(op.f("ix_offers_listing_id"), table_name="offers")
    op.drop_table("offers")
    op.drop_index(
        op.f("ix_negotiation_events_listing_id"), table_name="negotiation_events"
    )
    op.drop_table("negotiation_events")
    op.drop_index(op.f("ix_comps_listing_id"), table_name="comps")
    op.drop_index(op.f("ix_comps_external_id"), table_name="comps")
    op.drop_index(op.f("ix_comps_cluster_key"), table_name="comps")
    op.drop_table("comps")
    op.drop_index(op.f("ix_chats_seller_id"), table_name="chats")
    op.drop_index(op.f("ix_chats_listing_id"), table_name="chats")
    op.drop_index(op.f("ix_chats_avito_chat_id"), table_name="chats")
    op.drop_table("chats")
    op.drop_index(op.f("ix_listings_seller_id"), table_name="listings")
    op.drop_index(op.f("ix_listings_region"), table_name="listings")
    op.drop_index(op.f("ix_listings_district"), table_name="listings")
    op.drop_index(op.f("ix_listings_cadastral_number"), table_name="listings")
    op.drop_index(op.f("ix_listings_avito_item_id"), table_name="listings")
    op.drop_table("listings")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_sellers_phone"), table_name="sellers")
    op.drop_index(op.f("ix_sellers_avito_user_id"), table_name="sellers")
    op.drop_table("sellers")
    op.drop_index(op.f("ix_pipeline_stages_order_index"), table_name="pipeline_stages")
    op.drop_table("pipeline_stages")
    # Конец сгенерированного блока.
