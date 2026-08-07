from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar

from pydantic import UUID4, ConfigDict, field_validator
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household.pantry import PantryItem
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit
from mealie.schema.response.pagination import PaginationBase


class PantryItemCreate(MealieModel):
    name: str
    barcode: str | None = None
    quantity: float | None = None
    unit_id: UUID4 | None = None
    unit_text: str | None = None
    food_id: UUID4 | None = None
    category: str | None = None
    location: str | None = None
    tags: str | None = None
    notes: str | None = None
    product_image_url: str | None = None
    manufacturer: str | None = None
    ingredients: str | None = None
    nutrition_summary: str | None = None
    remaining: str | None = None
    expiration_date: date | None = None
    opened_date: date | None = None
    in_stock: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        return name

    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, barcode: str | None) -> str | None:
        barcode = barcode.strip() if barcode else None
        return barcode or None

    @field_validator("remaining")
    @classmethod
    def validate_remaining(cls, remaining: str | None) -> str | None:
        remaining = remaining.strip() if remaining else None
        return remaining or None


class PantryItemSave(PantryItemCreate):
    group_id: UUID4
    household_id: UUID4


class PantryItemUpdate(PantryItemSave):
    id: UUID4


class PantryItemOut(PantryItemUpdate):
    _searchable_properties: ClassVar[list[str]] = [
        "name",
        "barcode",
        "category",
        "location",
        "tags",
        "notes",
        "manufacturer",
        "ingredients",
        "remaining",
    ]

    food: IngredientFood | None = None
    unit: IngredientUnit | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(PantryItem.food), joinedload(PantryItem.unit)]


class PantryItemPagination(PaginationBase):
    items: list[PantryItemOut]


class PantryItemHistoryCreate(MealieModel):
    remaining: str
    note: str | None = None
    checked_at: datetime | None = None

    @field_validator("remaining")
    @classmethod
    def validate_remaining(cls, remaining: str) -> str:
        remaining = remaining.strip()
        if not remaining:
            raise ValueError("Remaining cannot be empty")
        return remaining

    @field_validator("note")
    @classmethod
    def validate_note(cls, note: str | None) -> str | None:
        note = note.strip() if note else None
        return note or None


class PantryItemHistoryOut(PantryItemHistoryCreate):
    id: UUID4
    group_id: UUID4
    household_id: UUID4
    pantry_item_id: UUID4
    created_at: datetime | None = None
    updated_at: datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)


class PantryItemPriceHistoryCreate(MealieModel):
    price: Decimal
    currency: str = "USD"
    store: str | None = None
    quantity: float | None = None
    unit_text: str | None = None
    note: str | None = None
    purchased_at: datetime | None = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, price: Decimal) -> Decimal:
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, currency: str) -> str:
        currency = currency.strip().upper()
        if not currency:
            raise ValueError("Currency cannot be empty")
        return currency

    @field_validator("store", "unit_text", "note")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        value = value.strip() if value else None
        return value or None


class PantryItemPriceHistoryOut(PantryItemPriceHistoryCreate):
    id: UUID4
    group_id: UUID4
    household_id: UUID4
    pantry_item_id: UUID4
    created_at: datetime | None = None
    updated_at: datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)
