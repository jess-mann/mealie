"""add pantry items

Revision ID: 6f2f9d0a7c31
Revises: 2187537c52b8
Create Date: 2026-08-04 14:35:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "6f2f9d0a7c31"
down_revision: str | None = "2187537c52b8"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "pantry_items",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("food_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("unit_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_text", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("tags", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("opened_date", sa.Date(), nullable=True),
        sa.Column("in_stock", sa.Boolean(), nullable=False),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(["food_id"], ["ingredient_foods.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["ingredient_units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pantry_items_category"), "pantry_items", ["category"], unique=False)
    op.create_index(op.f("ix_pantry_items_created_at"), "pantry_items", ["created_at"], unique=False)
    op.create_index(op.f("ix_pantry_items_expiration_date"), "pantry_items", ["expiration_date"], unique=False)
    op.create_index(op.f("ix_pantry_items_food_id"), "pantry_items", ["food_id"], unique=False)
    op.create_index(op.f("ix_pantry_items_group_id"), "pantry_items", ["group_id"], unique=False)
    op.create_index(op.f("ix_pantry_items_household_id"), "pantry_items", ["household_id"], unique=False)
    op.create_index(op.f("ix_pantry_items_in_stock"), "pantry_items", ["in_stock"], unique=False)
    op.create_index(op.f("ix_pantry_items_location"), "pantry_items", ["location"], unique=False)
    op.create_index(op.f("ix_pantry_items_name"), "pantry_items", ["name"], unique=False)
    op.create_index(op.f("ix_pantry_items_unit_id"), "pantry_items", ["unit_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pantry_items_unit_id"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_name"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_location"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_in_stock"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_household_id"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_group_id"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_food_id"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_expiration_date"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_created_at"), table_name="pantry_items")
    op.drop_index(op.f("ix_pantry_items_category"), table_name="pantry_items")
    op.drop_table("pantry_items")
