from datetime import UTC, datetime
from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy import select

from mealie.db.models.household.pantry import PantryItem, PantryItemHistory, PantryItemPriceHistory
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.household.pantry import (
    PantryItemCreate,
    PantryItemHistoryCreate,
    PantryItemHistoryOut,
    PantryItemOut,
    PantryItemPagination,
    PantryItemPriceHistoryCreate,
    PantryItemPriceHistoryOut,
    PantryItemSave,
    PantryItemUpdate,
)
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/households/pantry/items", tags=["Households: Pantry Items"])


@controller(router)
class PantryItemController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.pantry_items

    @cached_property
    def mixins(self):
        return HttpRepo[PantryItemCreate, PantryItemOut, PantryItemSave](self.repo, self.logger)

    def _get_item_model(self, item_id: UUID4):
        item = self.session.scalar(
            select(PantryItem).where(
                PantryItem.id == item_id,
                PantryItem.group_id == self.group_id,
                PantryItem.household_id == self.household_id,
            )
        )

        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found.")

        return item

    @router.get("", response_model=PantryItemPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=PantryItemOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=PantryItemOut, status_code=status.HTTP_201_CREATED)
    def create_one(self, data: PantryItemCreate):
        save = data.cast(PantryItemSave, group_id=self.group_id, household_id=self.household_id)
        return self.mixins.create_one(save)

    @router.get("/{item_id}", response_model=PantryItemOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=PantryItemOut)
    def update_one(self, item_id: UUID4, data: PantryItemCreate):
        save = data.cast(PantryItemUpdate, id=item_id, group_id=self.group_id, household_id=self.household_id)
        return self.mixins.update_one(save, item_id)

    @router.get("/{item_id}/history", response_model=list[PantryItemHistoryOut])
    def get_history(self, item_id: UUID4):
        self._get_item_model(item_id)

        return self.session.scalars(
            select(PantryItemHistory)
            .where(
                PantryItemHistory.pantry_item_id == item_id,
                PantryItemHistory.group_id == self.group_id,
                PantryItemHistory.household_id == self.household_id,
            )
            .order_by(PantryItemHistory.checked_at.desc(), PantryItemHistory.created_at.desc())
        ).all()

    @router.post("/{item_id}/history", response_model=PantryItemHistoryOut, status_code=status.HTTP_201_CREATED)
    def create_history(self, item_id: UUID4, data: PantryItemHistoryCreate):
        item = self._get_item_model(item_id)

        remaining = data.remaining.strip()
        history = PantryItemHistory(
            group_id=self.group_id,
            household_id=self.household_id,
            pantry_item_id=item_id,
            remaining=remaining,
            note=data.note,
            checked_at=data.checked_at or datetime.now(UTC),
            session=self.session,
        )
        item.remaining = remaining
        if remaining.lower() in {"out", "empty", "none", "0", "0%"}:
            item.in_stock = False
        else:
            item.in_stock = True

        self.session.add(history)
        self.session.commit()
        self.session.refresh(history)
        return history

    @router.get("/{item_id}/prices", response_model=list[PantryItemPriceHistoryOut])
    def get_prices(self, item_id: UUID4):
        self._get_item_model(item_id)

        return self.session.scalars(
            select(PantryItemPriceHistory)
            .where(
                PantryItemPriceHistory.pantry_item_id == item_id,
                PantryItemPriceHistory.group_id == self.group_id,
                PantryItemPriceHistory.household_id == self.household_id,
            )
            .order_by(PantryItemPriceHistory.purchased_at.desc(), PantryItemPriceHistory.created_at.desc())
        ).all()

    @router.post("/{item_id}/prices", response_model=PantryItemPriceHistoryOut, status_code=status.HTTP_201_CREATED)
    def create_price(self, item_id: UUID4, data: PantryItemPriceHistoryCreate):
        self._get_item_model(item_id)

        price = PantryItemPriceHistory(
            group_id=self.group_id,
            household_id=self.household_id,
            pantry_item_id=item_id,
            price=data.price,
            currency=data.currency,
            store=data.store,
            quantity=data.quantity,
            unit_text=data.unit_text,
            note=data.note,
            purchased_at=data.purchased_at or datetime.now(UTC),
            session=self.session,
        )

        self.session.add(price)
        self.session.commit()
        self.session.refresh(price)
        return price

    @router.delete("/{item_id}", response_model=PantryItemOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)
