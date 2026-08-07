from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar

from pydantic import UUID4, ConfigDict, Field, field_validator, model_validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household.receipt import Receipt
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.response.pagination import PaginationBase


class ReceiptLineItemCreate(MealieModel):
    raw_text: str | None = None
    name: str
    quantity: float | None = None
    unit_text: str | None = None
    unit_price: Decimal | None = None
    total_price: Decimal
    discount: Decimal | None = None
    product_code: str | None = None
    category: str | None = None
    confidence: float | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        return name

    @field_validator("total_price", "unit_price", "discount")
    @classmethod
    def validate_money(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("Amount cannot be negative")
        return value

    @field_validator("raw_text", "unit_text", "product_code", "category", "notes")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        value = value.strip() if value else None
        return value or None


class ReceiptLineItemSave(ReceiptLineItemCreate):
    group_id: UUID4
    household_id: UUID4
    receipt_id: UUID4
    position: int = 0


class ReceiptLineItemOut(ReceiptLineItemSave):
    id: UUID4
    created_at: datetime | None = None
    updated_at: datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)


class ReceiptCreate(MealieModel):
    merchant_name: str
    purchased_at: datetime | None = None
    receipt_date: date | None = None
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None
    currency: str = "USD"
    status: str = "manual"
    image_url: str | None = None
    image_filename: str | None = None
    raw_text: str | None = None
    ocr_text: str | None = None
    ocr_status: str | None = None
    ocr_engine: str | None = None
    parser_name: str | None = None
    parser_version: str | None = None
    parser_output: str | None = None
    parser_warnings: str | None = None
    notes: str | None = None
    items: list[ReceiptLineItemCreate] = Field(default_factory=list)

    @field_validator("merchant_name")
    @classmethod
    def validate_merchant_name(cls, merchant_name: str) -> str:
        merchant_name = merchant_name.strip()
        if not merchant_name:
            raise ValueError("Merchant cannot be empty")
        return merchant_name

    @field_validator("subtotal", "tax", "total")
    @classmethod
    def validate_money(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("Amount cannot be negative")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, currency: str) -> str:
        currency = currency.strip().upper()
        if not currency:
            raise ValueError("Currency cannot be empty")
        return currency

    @field_validator("status")
    @classmethod
    def validate_status(cls, status: str) -> str:
        status = status.strip().lower()
        if not status:
            raise ValueError("Status cannot be empty")
        return status

    @field_validator(
        "image_url",
        "image_filename",
        "raw_text",
        "ocr_text",
        "ocr_status",
        "ocr_engine",
        "parser_name",
        "parser_version",
        "parser_output",
        "parser_warnings",
        "notes",
    )
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        value = value.strip() if value else None
        return value or None

    @model_validator(mode="after")
    def set_receipt_date(self):
        if self.receipt_date is None and self.purchased_at is not None:
            self.receipt_date = self.purchased_at.date()
        return self


class ReceiptSave(ReceiptCreate):
    group_id: UUID4
    household_id: UUID4


class ReceiptUpdate(ReceiptSave):
    id: UUID4


class ReceiptOut(ReceiptUpdate):
    _searchable_properties: ClassVar[list[str]] = [
        "merchant_name",
        "status",
        "currency",
        "raw_text",
        "notes",
    ]

    items: list[ReceiptLineItemOut] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [selectinload(Receipt.items), joinedload(Receipt.group), joinedload(Receipt.household)]


class ReceiptPagination(PaginationBase):
    items: list[ReceiptOut]
