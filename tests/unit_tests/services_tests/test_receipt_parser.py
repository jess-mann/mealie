from decimal import Decimal

from mealie.services.receipts.parser import parse_receipt_text


def test_parse_receipt_text_ignores_phone_number_lines():
    parsed = parse_receipt_text(
        "\n".join(
            [
                "TRADER JOE'S",
                "941-922-5727",
                "TOPICI BIANCO FISH BOTTLE",
                "$23.98",
                "TOTAL PURCHASE",
                "$25.66",
            ]
        )
    )

    assert all(item["rawText"] != "941-922-5727" for item in parsed.items)


def test_parse_receipt_text_pairs_labels_and_amounts_on_next_line():
    parsed = parse_receipt_text(
        "\n".join(
            [
                "TRADER JOE'S",
                "TOPICI BIANCO FISH BOTTLE",
                "$23.98",
                "Tax:",
                "$1.68",
                "TOTAL PURCHASE",
                "$25.66",
                "AMEX",
                "$25.66",
            ]
        )
    )

    assert parsed.tax == Decimal("1.68")
    assert parsed.total == Decimal("25.66")
    assert [item["name"] for item in parsed.items] == ["Topici Bianco Fish Bottle"]


def test_parse_receipt_text_attaches_quantity_unit_price_to_previous_item():
    parsed = parse_receipt_text(
        "\n".join(
            [
                "TRADER JOE'S",
                "T OPICI BIANCO FISH BOTTLE",
                "$23.98",
                "2@$11.99",
                "OPICI BIANCO FISH BOTTLE",
                "$23.98",
                "2$11.99",
                "TOTAL PURCHASE",
                "$25.66",
            ]
        )
    )

    assert [item["name"] for item in parsed.items] == [
        "T Opici Bianco Fish Bottle",
        "Opici Bianco Fish Bottle",
    ]
    assert [item["quantity"] for item in parsed.items] == ["2", "2"]
    assert [item["unitPrice"] for item in parsed.items] == ["11.99", "11.99"]


def test_parse_receipt_text_ignores_smushed_quantity_unit_price_without_separator():
    parsed = parse_receipt_text(
        "\n".join(
            [
                "TRADER JOE'S",
                "T OPICI BIANCO FISH BOTTLE",
                "$23.98",
                "20511.99",
                "TOTAL PURCHASE",
                "$25.66",
            ]
        )
    )

    assert [item["name"] for item in parsed.items] == ["T Opici Bianco Fish Bottle"]
