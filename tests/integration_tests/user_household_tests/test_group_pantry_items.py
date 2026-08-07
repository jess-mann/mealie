from fastapi.testclient import TestClient

from tests import utils
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def pantry_payload(**overrides):
    return {
        "name": "Black Beans",
        "barcode": "012345678905",
        "quantity": 4,
        "unitText": "cans",
        "category": "Beans",
        "location": "Pantry",
        "tags": "quick dinner, shelf stable",
        "notes": "Great with cilantro lime rice.",
        "productImageUrl": "https://example.com/black-beans.jpg",
        "manufacturer": "Bean Farm",
        "ingredients": "Black beans, water, salt.",
        "nutritionSummary": "Energy 91 kcal, Protein 6 g.",
        "remaining": "full",
        "expirationDate": "2026-12-31",
        "openedDate": None,
        "inStock": True,
        **overrides,
    }


def test_pantry_items_crud(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.households_pantry_items, json=pantry_payload(), headers=unique_user.token)
    created = utils.assert_deserialize(response, 201)

    assert created["name"] == "Black Beans"
    assert created["groupId"] == str(unique_user.group_id)
    assert created["householdId"] == str(unique_user.household_id)
    assert created["barcode"] == "012345678905"
    assert created["productImageUrl"] == "https://example.com/black-beans.jpg"
    assert created["manufacturer"] == "Bean Farm"
    assert created["ingredients"] == "Black beans, water, salt."
    assert created["nutritionSummary"] == "Energy 91 kcal, Protein 6 g."
    assert created["remaining"] == "full"
    assert created["inStock"] is True

    item_id = created["id"]

    response = api_client.get(api_routes.households_pantry_items_item_id(item_id), headers=unique_user.token)
    fetched = utils.assert_deserialize(response)
    assert fetched["id"] == item_id

    response = api_client.get(
        api_routes.households_pantry_items,
        params={"search": "012345678905"},
        headers=unique_user.token,
    )
    page = utils.assert_deserialize(response)
    assert item_id in [item["id"] for item in page["items"]]

    update = pantry_payload(name="Black Beans, Low Sodium", quantity=2, inStock=False)
    update["id"] = item_id
    update["groupId"] = str(unique_user.group_id)
    update["householdId"] = str(unique_user.household_id)

    response = api_client.put(
        api_routes.households_pantry_items_item_id(item_id), json=update, headers=unique_user.token
    )
    updated = utils.assert_deserialize(response)
    assert updated["name"] == "Black Beans, Low Sodium"
    assert updated["quantity"] == 2
    assert updated["inStock"] is False

    response = api_client.delete(api_routes.households_pantry_items_item_id(item_id), headers=unique_user.token)
    utils.assert_deserialize(response)

    response = api_client.get(api_routes.households_pantry_items_item_id(item_id), headers=unique_user.token)
    assert response.status_code == 404


def test_pantry_item_history(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.households_pantry_items, json=pantry_payload(), headers=unique_user.token)
    created = utils.assert_deserialize(response, 201)
    item_id = created["id"]

    response = api_client.post(
        api_routes.households_pantry_items_item_id_history(item_id),
        json={"remaining": "half left", "note": "Used some for lunch.", "checkedAt": "2026-08-03T12:00:00"},
        headers=unique_user.token,
    )
    history = utils.assert_deserialize(response, 201)
    assert history["pantryItemId"] == item_id
    assert history["remaining"] == "half left"
    assert history["note"] == "Used some for lunch."

    response = api_client.get(api_routes.households_pantry_items_item_id(item_id), headers=unique_user.token)
    fetched = utils.assert_deserialize(response)
    assert fetched["remaining"] == "half left"
    assert fetched["inStock"] is True

    response = api_client.post(
        api_routes.households_pantry_items_item_id_history(item_id),
        json={"remaining": "out"},
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 201)

    response = api_client.get(api_routes.households_pantry_items_item_id(item_id), headers=unique_user.token)
    fetched = utils.assert_deserialize(response)
    assert fetched["remaining"] == "out"
    assert fetched["inStock"] is False

    response = api_client.get(api_routes.households_pantry_items_item_id_history(item_id), headers=unique_user.token)
    page = utils.assert_deserialize(response)
    assert [entry["remaining"] for entry in page] == ["out", "half left"]


def test_pantry_item_price_history(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.households_pantry_items, json=pantry_payload(), headers=unique_user.token)
    created = utils.assert_deserialize(response, 201)
    item_id = created["id"]

    response = api_client.post(
        api_routes.households_pantry_items_item_id_prices(item_id),
        json={
            "price": "1.29",
            "currency": "usd",
            "store": "Corner Market",
            "quantity": 1,
            "unitText": "can",
            "note": "Sale price",
            "purchasedAt": "2026-08-03T12:00:00",
        },
        headers=unique_user.token,
    )
    price = utils.assert_deserialize(response, 201)
    assert price["pantryItemId"] == item_id
    assert price["price"] == "1.29"
    assert price["currency"] == "USD"
    assert price["store"] == "Corner Market"
    assert price["unitText"] == "can"

    response = api_client.post(
        api_routes.households_pantry_items_item_id_prices(item_id),
        json={"price": "1.49", "store": "Grocery Co"},
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 201)

    response = api_client.get(api_routes.households_pantry_items_item_id_prices(item_id), headers=unique_user.token)
    page = utils.assert_deserialize(response)
    assert [entry["price"] for entry in page] == ["1.49", "1.29"]
    assert [entry["store"] for entry in page] == ["Grocery Co", "Corner Market"]


def test_create_pantry_item_bad_name(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(
        api_routes.households_pantry_items, json=pantry_payload(name=" "), headers=unique_user.token
    )
    assert response.status_code == 422
