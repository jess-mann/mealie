import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types


revision = "b1c2d3e4f5a6"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pantry_item_price_history",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("pantry_item_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("store", sa.String(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_text", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("purchased_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.ForeignKeyConstraint(["pantry_item_id"], ["pantry_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pantry_item_price_history_currency"),
        "pantry_item_price_history",
        ["currency"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pantry_item_price_history_group_id"),
        "pantry_item_price_history",
        ["group_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pantry_item_price_history_household_id"),
        "pantry_item_price_history",
        ["household_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pantry_item_price_history_pantry_item_id"),
        "pantry_item_price_history",
        ["pantry_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pantry_item_price_history_purchased_at"),
        "pantry_item_price_history",
        ["purchased_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pantry_item_price_history_store"),
        "pantry_item_price_history",
        ["store"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pantry_item_price_history_store"), table_name="pantry_item_price_history")
    op.drop_index(op.f("ix_pantry_item_price_history_purchased_at"), table_name="pantry_item_price_history")
    op.drop_index(op.f("ix_pantry_item_price_history_pantry_item_id"), table_name="pantry_item_price_history")
    op.drop_index(op.f("ix_pantry_item_price_history_household_id"), table_name="pantry_item_price_history")
    op.drop_index(op.f("ix_pantry_item_price_history_group_id"), table_name="pantry_item_price_history")
    op.drop_index(op.f("ix_pantry_item_price_history_currency"), table_name="pantry_item_price_history")
    op.drop_table("pantry_item_price_history")
