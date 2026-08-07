import sqlalchemy as sa
from alembic import op


revision = "b8c7e3d2a941"
down_revision = "6f2f9d0a7c31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pantry_items", sa.Column("barcode", sa.String(), nullable=True))
    op.create_index(op.f("ix_pantry_items_barcode"), "pantry_items", ["barcode"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pantry_items_barcode"), table_name="pantry_items")
    op.drop_column("pantry_items", "barcode")
