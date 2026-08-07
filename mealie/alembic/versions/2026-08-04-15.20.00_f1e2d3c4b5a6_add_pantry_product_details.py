import sqlalchemy as sa
from alembic import op


revision = "f1e2d3c4b5a6"
down_revision = "b8c7e3d2a941"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pantry_items", sa.Column("product_image_url", sa.String(), nullable=True))
    op.add_column("pantry_items", sa.Column("manufacturer", sa.String(), nullable=True))
    op.add_column("pantry_items", sa.Column("ingredients", sa.String(), nullable=True))
    op.add_column("pantry_items", sa.Column("nutrition_summary", sa.String(), nullable=True))
    op.create_index(op.f("ix_pantry_items_manufacturer"), "pantry_items", ["manufacturer"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pantry_items_manufacturer"), table_name="pantry_items")
    op.drop_column("pantry_items", "nutrition_summary")
    op.drop_column("pantry_items", "ingredients")
    op.drop_column("pantry_items", "manufacturer")
    op.drop_column("pantry_items", "product_image_url")
