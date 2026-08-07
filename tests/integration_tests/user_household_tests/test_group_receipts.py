from fastapi.testclient import TestClient

from mealie.routes.households import controller_receipts
from mealie.services.receipts.ocr import ReceiptOcrResult
from mealie.services.receipts.parser import ParsedReceipt
from tests import utils
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def receipt_payload(**overrides):
    return {
        "merchantName": "Walmart",
        "purchasedAt": "2026-08-06T12:00:00",
        "receiptDate": "2026-08-06",
        "subtotal": "4.26",
        "tax": "0.31",
        "total": "4.57",
        "currency": "usd",
        "status": "manual",
        "rawText": "BANANAS 1.28\nMILK 2.98",
        "notes": "First manual receipt.",
        "items": [
            {
                "rawText": "BANANAS 1.28",
                "name": "Bananas",
                "quantity": 1,
                "unitText": "bunch",
                "unitPrice": "1.28",
                "totalPrice": "1.28",
                "category": "Produce",
            },
            {
                "rawText": "MILK 2.98",
                "name": "Milk",
                "quantity": 1,
                "unitText": "carton",
                "unitPrice": "2.98",
                "totalPrice": "2.98",
                "productCode": "093966515008",
                "category": "Dairy",
            },
        ],
        **overrides,
    }


def test_receipts_crud(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.households_receipts, json=receipt_payload(), headers=unique_user.token)
    created = utils.assert_deserialize(response, 201)

    assert created["merchantName"] == "Walmart"
    assert created["groupId"] == str(unique_user.group_id)
    assert created["householdId"] == str(unique_user.household_id)
    assert created["currency"] == "USD"
    assert created["status"] == "manual"
    assert created["total"] == "4.57"
    assert [item["name"] for item in created["items"]] == ["Bananas", "Milk"]
    assert created["items"][1]["productCode"] == "093966515008"

    receipt_id = created["id"]

    response = api_client.get(api_routes.households_receipts_receipt_id(receipt_id), headers=unique_user.token)
    fetched = utils.assert_deserialize(response)
    assert fetched["id"] == receipt_id
    assert len(fetched["items"]) == 2

    response = api_client.get(
        api_routes.households_receipts,
        params={"search": "milk"},
        headers=unique_user.token,
    )
    page = utils.assert_deserialize(response)
    assert receipt_id in [receipt["id"] for receipt in page["items"]]

    update = receipt_payload(
        merchantName="Target",
        total="5.00",
        items=[
            {
                "rawText": "STRAWBERRIES 5.00",
                "name": "Strawberries",
                "quantity": 1,
                "unitText": "clamshell",
                "totalPrice": "5.00",
                "category": "Produce",
            }
        ],
    )
    update["id"] = receipt_id
    update["groupId"] = str(unique_user.group_id)
    update["householdId"] = str(unique_user.household_id)

    response = api_client.put(
        api_routes.households_receipts_receipt_id(receipt_id), json=update, headers=unique_user.token
    )
    updated = utils.assert_deserialize(response)
    assert updated["merchantName"] == "Target"
    assert updated["total"] == "5.00"
    assert [item["name"] for item in updated["items"]] == ["Strawberries"]

    response = api_client.delete(api_routes.households_receipts_receipt_id(receipt_id), headers=unique_user.token)
    utils.assert_deserialize(response)

    response = api_client.get(api_routes.households_receipts_receipt_id(receipt_id), headers=unique_user.token)
    assert response.status_code == 404


def test_create_receipt_bad_merchant(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(
        api_routes.households_receipts,
        json=receipt_payload(merchantName=" "),
        headers=unique_user.token,
    )
    assert response.status_code == 422


def test_upload_receipt_image_stores_ocr_and_parser_output(api_client: TestClient, unique_user: TestUser, monkeypatch):
    monkeypatch.setattr(
        controller_receipts,
        "extract_receipt_text",
        lambda _: ReceiptOcrResult(
            text="WALMART\nBANANAS 1.28\nMILK 2.98\nSUBTOTAL 4.26\nTAX 0.31\nTOTAL 4.57",
            status="completed",
            engine="test-ocr",
            warnings=[],
        ),
    )

    response = api_client.post(
        api_routes.households_receipts,
        json=receipt_payload(merchantName="Receipt Upload", items=[]),
        headers=unique_user.token,
    )
    created = utils.assert_deserialize(response, 201)

    response = api_client.post(
        api_routes.households_receipts_receipt_id_image(created["id"]),
        files={"image": ("receipt.png", b"not-real-image-but-upload-route-does-not-decode", "image/png")},
        headers=unique_user.token,
    )
    uploaded = utils.assert_deserialize(response)

    assert uploaded["merchantName"] == "Walmart"
    assert uploaded["imageUrl"].endswith(f"/api/media/households/receipts/{created['id']}/image/original.png")
    assert uploaded["imageFilename"] == "original.png"
    assert uploaded["ocrStatus"] == "completed"
    assert uploaded["ocrEngine"] == "test-ocr"
    assert uploaded["ocrText"].startswith("WALMART")
    assert uploaded["parserName"] == "deterministic-line-parser"
    assert '"total": "4.57"' in uploaded["parserOutput"]
    assert [item["name"] for item in uploaded["items"]] == ["Bananas", "Milk"]


def test_upload_receipt_image_skips_invalid_parsed_items(api_client: TestClient, unique_user: TestUser, monkeypatch):
    monkeypatch.setattr(
        controller_receipts,
        "extract_receipt_text",
        lambda _: ReceiptOcrResult(
            text="TRADER JOE'S\n941-922-5727",
            status="completed",
            engine="test-ocr",
            warnings=[],
        ),
    )
    monkeypatch.setattr(
        controller_receipts,
        "parse_receipt_text",
        lambda _: ParsedReceipt(
            merchant_name="Trader Joe's",
            items=[
                {
                    "rawText": "941-922-5727",
                    "name": "941-922",
                    "totalPrice": "-5727",
                    "confidence": 0.55,
                }
            ],
        ),
    )

    response = api_client.post(
        api_routes.households_receipts,
        json=receipt_payload(merchantName="Receipt Upload", items=[]),
        headers=unique_user.token,
    )
    created = utils.assert_deserialize(response, 201)

    response = api_client.post(
        api_routes.households_receipts_receipt_id_image(created["id"]),
        files={"image": ("receipt.png", b"not-real-image-but-upload-route-does-not-decode", "image/png")},
        headers=unique_user.token,
    )
    uploaded = utils.assert_deserialize(response)

    assert uploaded["merchantName"] == "Trader Joe's"
    assert uploaded["items"] == []
    assert "Skipped parsed receipt item" in uploaded["parserWarnings"]
