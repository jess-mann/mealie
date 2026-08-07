from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

revision: str = "a2b3c4d5e6f7"
down_revision: str | None = "f1e2d3c4b5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("pantry_items", sa.Column("remaining", sa.String(), nullable=True))
    op.create_index(op.f("ix_pantry_items_remaining"), "pantry_items", ["remaining"], unique=False)

    op.create_table(
        "pantry_item_history",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("pantry_item_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("remaining", sa.String(), nullable=False),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("checked_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.ForeignKeyConstraint(["pantry_item_id"], ["pantry_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pantry_item_history_group_id"), "pantry_item_history", ["group_id"], unique=False)
    op.create_index(op.f("ix_pantry_item_history_household_id"), "pantry_item_history", ["household_id"], unique=False)
    op.create_index(op.f("ix_pantry_item_history_pantry_item_id"), "pantry_item_history", ["pantry_item_id"], unique=False)
    op.create_index(op.f("ix_pantry_item_history_remaining"), "pantry_item_history", ["remaining"], unique=False)
    op.create_index(op.f("ix_pantry_item_history_checked_at"), "pantry_item_history", ["checked_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pantry_item_history_checked_at"), table_name="pantry_item_history")
    op.drop_index(op.f("ix_pantry_item_history_remaining"), table_name="pantry_item_history")
    op.drop_index(op.f("ix_pantry_item_history_pantry_item_id"), table_name="pantry_item_history")
    op.drop_index(op.f("ix_pantry_item_history_household_id"), table_name="pantry_item_history")
    op.drop_index(op.f("ix_pantry_item_history_group_id"), table_name="pantry_item_history")
    op.drop_table("pantry_item_history")

    op.drop_index(op.f("ix_pantry_items_remaining"), table_name="pantry_items")
    op.drop_column("pantry_items", "remaining")
