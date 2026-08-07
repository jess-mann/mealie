"""add receipt ocr fields

Revision ID: d7e8f9a0b1c2
Revises: c6d7e8f9a0b1
Create Date: 2026-08-06 13:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "d7e8f9a0b1c2"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("receipts", sa.Column("image_filename", sa.String(), nullable=True))
    op.add_column("receipts", sa.Column("ocr_text", sa.Text(), nullable=True))
    op.add_column("receipts", sa.Column("ocr_status", sa.String(), nullable=True))
    op.add_column("receipts", sa.Column("ocr_engine", sa.String(), nullable=True))
    op.add_column("receipts", sa.Column("parser_name", sa.String(), nullable=True))
    op.add_column("receipts", sa.Column("parser_version", sa.String(), nullable=True))
    op.add_column("receipts", sa.Column("parser_output", sa.Text(), nullable=True))
    op.add_column("receipts", sa.Column("parser_warnings", sa.Text(), nullable=True))
    op.create_index(op.f("ix_receipts_ocr_status"), "receipts", ["ocr_status"], unique=False)
    op.create_index(op.f("ix_receipts_parser_name"), "receipts", ["parser_name"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_receipts_parser_name"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_ocr_status"), table_name="receipts")
    op.drop_column("receipts", "parser_warnings")
    op.drop_column("receipts", "parser_output")
    op.drop_column("receipts", "parser_version")
    op.drop_column("receipts", "parser_name")
    op.drop_column("receipts", "ocr_engine")
    op.drop_column("receipts", "ocr_status")
    op.drop_column("receipts", "ocr_text")
    op.drop_column("receipts", "image_filename")
