"""add receipts

Revision ID: c6d7e8f9a0b1
Revises: b1c2d3e4f5a6
Create Date: 2026-08-06 09:30:00.000000
"""

import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

revision = "c6d7e8f9a0b1"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "receipts",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("merchant_name", sa.String(), nullable=False),
        sa.Column("purchased_at", sa.DateTime(), nullable=False),
        sa.Column("receipt_date", sa.Date(), nullable=True),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=True),
        sa.Column("tax", sa.Numeric(10, 2), nullable=True),
        sa.Column("total", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("raw_text", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_receipts_currency"), "receipts", ["currency"], unique=False)
    op.create_index(op.f("ix_receipts_group_id"), "receipts", ["group_id"], unique=False)
    op.create_index(op.f("ix_receipts_household_id"), "receipts", ["household_id"], unique=False)
    op.create_index(op.f("ix_receipts_merchant_name"), "receipts", ["merchant_name"], unique=False)
    op.create_index(op.f("ix_receipts_purchased_at"), "receipts", ["purchased_at"], unique=False)
    op.create_index(op.f("ix_receipts_receipt_date"), "receipts", ["receipt_date"], unique=False)
    op.create_index(op.f("ix_receipts_status"), "receipts", ["status"], unique=False)
    op.create_index(op.f("ix_receipts_total"), "receipts", ["total"], unique=False)

    op.create_table(
        "receipt_line_items",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("receipt_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_text", sa.String(), nullable=True),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount", sa.Numeric(10, 2), nullable=True),
        sa.Column("product_code", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.ForeignKeyConstraint(["receipt_id"], ["receipts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_receipt_line_items_category"), "receipt_line_items", ["category"], unique=False)
    op.create_index(op.f("ix_receipt_line_items_group_id"), "receipt_line_items", ["group_id"], unique=False)
    op.create_index(op.f("ix_receipt_line_items_household_id"), "receipt_line_items", ["household_id"], unique=False)
    op.create_index(op.f("ix_receipt_line_items_name"), "receipt_line_items", ["name"], unique=False)
    op.create_index(op.f("ix_receipt_line_items_position"), "receipt_line_items", ["position"], unique=False)
    op.create_index(op.f("ix_receipt_line_items_product_code"), "receipt_line_items", ["product_code"], unique=False)
    op.create_index(op.f("ix_receipt_line_items_receipt_id"), "receipt_line_items", ["receipt_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_receipt_line_items_receipt_id"), table_name="receipt_line_items")
    op.drop_index(op.f("ix_receipt_line_items_product_code"), table_name="receipt_line_items")
    op.drop_index(op.f("ix_receipt_line_items_position"), table_name="receipt_line_items")
    op.drop_index(op.f("ix_receipt_line_items_name"), table_name="receipt_line_items")
    op.drop_index(op.f("ix_receipt_line_items_household_id"), table_name="receipt_line_items")
    op.drop_index(op.f("ix_receipt_line_items_group_id"), table_name="receipt_line_items")
    op.drop_index(op.f("ix_receipt_line_items_category"), table_name="receipt_line_items")
    op.drop_table("receipt_line_items")

    op.drop_index(op.f("ix_receipts_total"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_status"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_receipt_date"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_purchased_at"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_merchant_name"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_household_id"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_group_id"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_currency"), table_name="receipts")
    op.drop_table("receipts")
