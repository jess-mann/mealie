import json
import shutil
from datetime import UTC, datetime
from functools import cached_property
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import UUID4, ValidationError
from sqlalchemy import select

from mealie.core.config import get_app_dirs
from mealie.db.models.household.receipt import Receipt, ReceiptLineItem
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.schema.household.receipt import (
    ReceiptCreate,
    ReceiptLineItemCreate,
    ReceiptOut,
    ReceiptPagination,
    ReceiptSave,
    ReceiptUpdate,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.receipts.ocr import extract_receipt_text
from mealie.services.receipts.parser import PARSER_NAME, PARSER_VERSION, parse_receipt_text

router = APIRouter(prefix="/households/receipts", tags=["Households: Receipts"])

IMAGE_EXTENSIONS_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
}


@controller(router)
class ReceiptController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.receipts

    def _get_receipt_model(self, receipt_id: UUID4):
        receipt = self.session.scalar(
            select(Receipt).where(
                Receipt.id == receipt_id,
                Receipt.group_id == self.group_id,
                Receipt.household_id == self.household_id,
            )
        )

        if not receipt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found.")

        return receipt

    def _set_line_items(self, receipt: Receipt, items):
        receipt.items.clear()
        for index, item in enumerate(items):
            receipt.items.append(
                ReceiptLineItem(
                    group_id=self.group_id,
                    household_id=self.household_id,
                    receipt_id=receipt.id,
                    position=index,
                    raw_text=item.raw_text,
                    name=item.name,
                    quantity=item.quantity,
                    unit_text=item.unit_text,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    discount=item.discount,
                    product_code=item.product_code,
                    category=item.category,
                    confidence=item.confidence,
                    notes=item.notes,
                    session=self.session,
                )
            )

    def _receipt_image_dir(self, receipt: Receipt) -> Path:
        return (
            get_app_dirs()
            .DATA_DIR.joinpath("receipts")
            .joinpath(str(receipt.group_id))
            .joinpath(str(receipt.household_id))
            .joinpath(str(receipt.id))
        )

    def _set_parsed_receipt(self, receipt: Receipt, ocr_text: str | None):
        parsed = parse_receipt_text(ocr_text)
        parser_output = parsed.as_dict()
        receipt.parser_name = PARSER_NAME
        receipt.parser_version = PARSER_VERSION
        receipt.parser_output = json.dumps(parser_output)
        receipt.parser_warnings = json.dumps(parser_output["warnings"])

        if parsed.merchant_name and receipt.merchant_name.lower() in {"receipt upload", "unknown merchant"}:
            receipt.merchant_name = parsed.merchant_name
        receipt.subtotal = receipt.subtotal or parsed.subtotal
        receipt.tax = receipt.tax or parsed.tax
        receipt.total = receipt.total or parsed.total
        line_items = []
        for item in parsed.items:
            try:
                line_items.append(ReceiptLineItemCreate(**item))
            except ValidationError as error:
                raw_text = item.get("rawText")
                message = error.errors()[0]["msg"]
                parser_output["warnings"].append(f"Skipped parsed receipt item '{raw_text}': {message}")

        receipt.parser_warnings = json.dumps(parser_output["warnings"])
        receipt.parser_output = json.dumps(parser_output)
        if line_items:
            self._set_line_items(receipt, line_items)

    @router.get("", response_model=ReceiptPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=ReceiptOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
    def create_one(self, data: ReceiptCreate):
        save = data.cast(ReceiptSave, group_id=self.group_id, household_id=self.household_id)
        receipt = Receipt(
            group_id=save.group_id,
            household_id=save.household_id,
            merchant_name=save.merchant_name,
            purchased_at=save.purchased_at or datetime.now(UTC),
            receipt_date=save.receipt_date,
            subtotal=save.subtotal,
            tax=save.tax,
            total=save.total,
            currency=save.currency,
            status=save.status,
            image_url=save.image_url,
            image_filename=save.image_filename,
            raw_text=save.raw_text,
            ocr_text=save.ocr_text,
            ocr_status=save.ocr_status,
            ocr_engine=save.ocr_engine,
            parser_name=save.parser_name,
            parser_version=save.parser_version,
            parser_output=save.parser_output,
            parser_warnings=save.parser_warnings,
            notes=save.notes,
            session=self.session,
        )
        self.session.add(receipt)
        self.session.flush()
        self._set_line_items(receipt, save.items)
        self.session.commit()
        self.session.refresh(receipt)
        return receipt

    @router.get("/{receipt_id}", response_model=ReceiptOut)
    def get_one(self, receipt_id: UUID4):
        return self._get_receipt_model(receipt_id)

    @router.put("/{receipt_id}", response_model=ReceiptOut)
    def update_one(self, receipt_id: UUID4, data: ReceiptCreate):
        save = data.cast(ReceiptUpdate, id=receipt_id, group_id=self.group_id, household_id=self.household_id)
        receipt = self._get_receipt_model(receipt_id)
        receipt.merchant_name = save.merchant_name
        receipt.purchased_at = save.purchased_at or receipt.purchased_at
        receipt.receipt_date = save.receipt_date
        receipt.subtotal = save.subtotal
        receipt.tax = save.tax
        receipt.total = save.total
        receipt.currency = save.currency
        receipt.status = save.status
        receipt.image_url = save.image_url
        receipt.image_filename = save.image_filename
        receipt.raw_text = save.raw_text
        receipt.ocr_text = save.ocr_text
        receipt.ocr_status = save.ocr_status
        receipt.ocr_engine = save.ocr_engine
        receipt.parser_name = save.parser_name
        receipt.parser_version = save.parser_version
        receipt.parser_output = save.parser_output
        receipt.parser_warnings = save.parser_warnings
        receipt.notes = save.notes
        self._set_line_items(receipt, save.items)
        self.session.commit()
        self.session.refresh(receipt)
        return receipt

    @router.post("/{receipt_id}/image", response_model=ReceiptOut)
    def upload_image(self, receipt_id: UUID4, image: UploadFile = File(...)):
        receipt = self._get_receipt_model(receipt_id)
        extension = IMAGE_EXTENSIONS_BY_CONTENT_TYPE.get(image.content_type or "")
        if extension is None:
            suffix = Path(image.filename or "").suffix.lower()
            extension = suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"} else None
        if extension is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported receipt image type.")

        dest_dir = self._receipt_image_dir(receipt)
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = f"original{extension}"
        dest = dest_dir.joinpath(filename).resolve()
        if not dest.is_relative_to(dest_dir.resolve()):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid receipt image path.")

        with dest.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        ocr = extract_receipt_text(dest)
        receipt.image_filename = filename
        receipt.image_url = f"/api/media/households/receipts/{receipt.id}/image/{filename}"
        receipt.ocr_status = ocr.status
        receipt.ocr_engine = ocr.engine
        receipt.ocr_text = ocr.text
        receipt.raw_text = ocr.text or receipt.raw_text
        self._set_parsed_receipt(receipt, ocr.text)

        warnings = json.loads(receipt.parser_warnings or "[]")
        warnings.extend(ocr.warnings)
        receipt.parser_warnings = json.dumps(warnings)
        receipt.status = "ocr_" + ocr.status

        self.session.commit()
        self.session.refresh(receipt)
        return receipt

    @router.delete("/{receipt_id}", response_model=ReceiptOut)
    def delete_one(self, receipt_id: UUID4):
        receipt = self._get_receipt_model(receipt_id)
        self.session.delete(receipt)
        self.session.commit()
        return receipt
