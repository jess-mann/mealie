from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pydantic import ConfigDict
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from .household import Household


class Receipt(SqlAlchemyBase, BaseMixins):
    __tablename__ = "receipts"

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="receipts")
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    household: Mapped["Household"] = orm.relationship("Household", back_populates="receipts")

    merchant_name: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    purchased_at: FilterableColumn[datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )
    receipt_date: FilterableColumn[date | None] = mapped_column(sa.Date, index=True)
    subtotal: FilterableColumn[Decimal | None] = mapped_column(sa.Numeric(10, 2))
    tax: FilterableColumn[Decimal | None] = mapped_column(sa.Numeric(10, 2))
    total: FilterableColumn[Decimal | None] = mapped_column(sa.Numeric(10, 2), index=True)
    currency: FilterableColumn[str] = mapped_column(sa.String, nullable=False, default="USD", index=True)
    status: FilterableColumn[str] = mapped_column(sa.String, nullable=False, default="manual", index=True)
    image_url: FilterableColumn[str | None] = mapped_column(sa.String)
    image_filename: FilterableColumn[str | None] = mapped_column(sa.String)
    raw_text: FilterableColumn[str | None] = mapped_column(sa.Text)
    ocr_text: FilterableColumn[str | None] = mapped_column(sa.Text)
    ocr_status: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    ocr_engine: FilterableColumn[str | None] = mapped_column(sa.String)
    parser_name: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    parser_version: FilterableColumn[str | None] = mapped_column(sa.String)
    parser_output: FilterableColumn[str | None] = mapped_column(sa.Text)
    parser_warnings: FilterableColumn[str | None] = mapped_column(sa.Text)
    notes: FilterableColumn[str | None] = mapped_column(sa.Text)

    items: Mapped[list["ReceiptLineItem"]] = orm.relationship(
        "ReceiptLineItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="ReceiptLineItem.position",
    )

    model_config = ConfigDict(exclude={"group", "household", "items"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ReceiptLineItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "receipt_line_items"

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    receipt_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receipt: Mapped[Receipt] = orm.relationship(Receipt, back_populates="items")

    position: FilterableColumn[int] = mapped_column(sa.Integer, nullable=False, default=0, index=True)
    raw_text: FilterableColumn[str | None] = mapped_column(sa.String)
    name: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    quantity: FilterableColumn[float | None] = mapped_column(sa.Float)
    unit_text: FilterableColumn[str | None] = mapped_column(sa.String)
    unit_price: FilterableColumn[Decimal | None] = mapped_column(sa.Numeric(10, 2))
    total_price: FilterableColumn[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    discount: FilterableColumn[Decimal | None] = mapped_column(sa.Numeric(10, 2))
    product_code: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    category: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    confidence: FilterableColumn[float | None] = mapped_column(sa.Float)
    notes: FilterableColumn[str | None] = mapped_column(sa.String)

    model_config = ConfigDict(exclude={"receipt"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass
