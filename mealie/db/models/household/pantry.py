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
from ..recipe.ingredient import IngredientFoodModel, IngredientUnitModel

if TYPE_CHECKING:
    from ..group import Group
    from .household import Household


class PantryItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "pantry_items"

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="pantry_items")
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    household: Mapped["Household"] = orm.relationship("Household", back_populates="pantry_items")

    food_id: FilterableColumn[GUID | None] = mapped_column(GUID, sa.ForeignKey("ingredient_foods.id"), index=True)
    food: Mapped[IngredientFoodModel | None] = orm.relationship(IngredientFoodModel, uselist=False)
    unit_id: FilterableColumn[GUID | None] = mapped_column(GUID, sa.ForeignKey("ingredient_units.id"), index=True)
    unit: Mapped[IngredientUnitModel | None] = orm.relationship(IngredientUnitModel, uselist=False)

    name: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    barcode: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    quantity: FilterableColumn[float | None] = mapped_column(sa.Float)
    unit_text: FilterableColumn[str | None] = mapped_column(sa.String)
    category: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    location: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    tags: FilterableColumn[str | None] = mapped_column(sa.String)
    notes: FilterableColumn[str | None] = mapped_column(sa.String)
    product_image_url: FilterableColumn[str | None] = mapped_column(sa.String)
    manufacturer: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    ingredients: FilterableColumn[str | None] = mapped_column(sa.String)
    nutrition_summary: FilterableColumn[str | None] = mapped_column(sa.String)
    remaining: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    expiration_date: FilterableColumn[date | None] = mapped_column(sa.Date, index=True)
    opened_date: FilterableColumn[date | None] = mapped_column(sa.Date)
    in_stock: FilterableColumn[bool] = mapped_column(sa.Boolean, nullable=False, default=True, index=True)
    history: Mapped[list["PantryItemHistory"]] = orm.relationship(
        "PantryItemHistory",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="desc(PantryItemHistory.checked_at)",
    )
    price_history: Mapped[list["PantryItemPriceHistory"]] = orm.relationship(
        "PantryItemPriceHistory",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="desc(PantryItemPriceHistory.purchased_at)",
    )

    model_config = ConfigDict(exclude={"group", "household", "food", "unit", "history", "price_history"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class PantryItemHistory(SqlAlchemyBase, BaseMixins):
    __tablename__ = "pantry_item_history"

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    pantry_item_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("pantry_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item: Mapped[PantryItem] = orm.relationship(PantryItem, back_populates="history")

    remaining: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    note: FilterableColumn[str | None] = mapped_column(sa.String)
    checked_at: FilterableColumn[datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    model_config = ConfigDict(exclude={"item"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class PantryItemPriceHistory(SqlAlchemyBase, BaseMixins):
    __tablename__ = "pantry_item_price_history"

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    pantry_item_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("pantry_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item: Mapped[PantryItem] = orm.relationship(PantryItem, back_populates="price_history")

    price: FilterableColumn[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    currency: FilterableColumn[str] = mapped_column(sa.String, nullable=False, default="USD", index=True)
    store: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    quantity: FilterableColumn[float | None] = mapped_column(sa.Float)
    unit_text: FilterableColumn[str | None] = mapped_column(sa.String)
    note: FilterableColumn[str | None] = mapped_column(sa.String)
    purchased_at: FilterableColumn[datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    model_config = ConfigDict(exclude={"item"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass
