from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

PARSER_NAME = "deterministic-line-parser"
PARSER_VERSION = "0.1.0"

MONEY_RE = re.compile(r"(?<![\d-])(?P<amount>\$?\d+[.,]\d{2})\s*$")
QUANTITY_UNIT_PRICE_RE = re.compile(
    r"^\s*(?P<quantity>\d+(?:[.,]\d+)?)\s*(?:@|x)?\s*\$(?P<unit_price>\d+[.,]\d{2})\s*$",
    re.IGNORECASE,
)
TOTAL_RE = re.compile(r"\b(total|amount due|balance)\b", re.IGNORECASE)
SUBTOTAL_RE = re.compile(r"\b(subtotal|sub total)\b", re.IGNORECASE)
TAX_RE = re.compile(r"\b(tax|sales tax)\b", re.IGNORECASE)
SKIP_ITEM_RE = re.compile(
    r"\b(total|subtotal|sub total|tax|cash|change|visa|mastercard|amex|debit|credit|payment|auth|mid|tid|"
    r"items? in transact|customer copy|cardholder|verification|retain|records|store|till|trans|date|thank|www)\b",
    re.IGNORECASE,
)


@dataclass
class ParsedReceipt:
    merchant_name: str | None = None
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None
    items: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "merchantName": self.merchant_name,
            "subtotal": str(self.subtotal) if self.subtotal is not None else None,
            "tax": str(self.tax) if self.tax is not None else None,
            "total": str(self.total) if self.total is not None else None,
            "items": self.items,
            "warnings": self.warnings,
            "parser": {"name": PARSER_NAME, "version": PARSER_VERSION},
        }


def parse_receipt_text(text: str | None) -> ParsedReceipt:
    parsed = ParsedReceipt()
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]

    if not lines:
        parsed.warnings.append("No OCR text was available to parse.")
        return parsed

    parsed.merchant_name = _merchant_from_lines(lines)
    pending_amount_field: str | None = None
    pending_item_name: str | None = None

    for line in lines:
        quantity_unit_price = _quantity_unit_price_from_line(line)
        if quantity_unit_price is not None:
            if parsed.items:
                quantity, unit_price = quantity_unit_price
                parsed.items[-1]["quantity"] = str(quantity)
                parsed.items[-1]["unitPrice"] = str(unit_price)
                parsed.items[-1]["rawText"] = f"{parsed.items[-1]['rawText']}\n{line}"
            continue

        amount = _amount_from_line(line)
        if amount is None:
            if SUBTOTAL_RE.search(line):
                pending_amount_field = "subtotal"
                pending_item_name = None
            elif TAX_RE.search(line):
                pending_amount_field = "tax"
                pending_item_name = None
            elif TOTAL_RE.search(line):
                pending_amount_field = "total"
                pending_item_name = None
            elif SKIP_ITEM_RE.search(line):
                pending_item_name = None
            elif not SKIP_ITEM_RE.search(line) and not MONEY_RE.search(line):
                pending_item_name = line
            continue

        if pending_amount_field == "subtotal":
            parsed.subtotal = amount
            pending_amount_field = None
        elif pending_amount_field == "tax":
            parsed.tax = amount
            pending_amount_field = None
        elif pending_amount_field == "total":
            parsed.total = amount
            pending_amount_field = None
        elif SUBTOTAL_RE.search(line):
            parsed.subtotal = amount
        elif TAX_RE.search(line):
            parsed.tax = amount
        elif TOTAL_RE.search(line):
            parsed.total = amount
        elif not SKIP_ITEM_RE.search(line):
            name = MONEY_RE.sub("", line).strip(" -:$\t")
            if not name and pending_item_name:
                name = pending_item_name
                pending_item_name = None
            if name:
                parsed.items.append(
                    {
                        "rawText": line,
                        "name": _normalize_item_name(name),
                        "totalPrice": str(amount),
                        "confidence": 0.55,
                    }
                )

    if parsed.total is None and parsed.items:
        parsed.warnings.append("No explicit total line was found.")

    return parsed


def _merchant_from_lines(lines: list[str]) -> str | None:
    for line in lines[:5]:
        if MONEY_RE.search(line):
            continue
        if len(line) >= 3:
            return line.title()
    return None


def _amount_from_line(line: str) -> Decimal | None:
    match = MONEY_RE.search(line)
    if not match:
        return None

    value = match.group("amount").replace("$", "").replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _quantity_unit_price_from_line(line: str) -> tuple[Decimal, Decimal] | None:
    match = QUANTITY_UNIT_PRICE_RE.search(line)
    if not match:
        return None

    try:
        quantity = Decimal(match.group("quantity").replace(",", "."))
        unit_price = Decimal(match.group("unit_price").replace(",", "."))
    except InvalidOperation:
        return None

    return quantity, unit_price


def _normalize_item_name(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().title()
