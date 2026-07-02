"""
tests/test_inventory.py — Phase 1.5 inventory intake tests.
Routes live under /api/v1/inventory
"""

from datetime import date, timedelta

from tests.conftest import API, MILK_PRODUCT

TODAY = date.today()


def _p(path=""):
    return f"{API}/products{path}"


def _i(path=""):
    return f"{API}/inventory{path}"


def _create_product(client):
    client.post(_p(), json=MILK_PRODUCT)


def _intake(client, expiry_date=None, manufacturing_date="2026-01-01"):
    payload = {"barcode": "8901234567890", "batch_number": "BATCH001"}
    if manufacturing_date:
        payload["manufacturing_date"] = manufacturing_date
    if expiry_date:
        payload["expiry_date"] = expiry_date
    return client.post(_i("/intake"), json=payload)


# ── Test 1: ACCEPTED ─────────────────────────────────────────

def test_intake_valid_expiry_returns_accepted(client):
    _create_product(client)
    r = _intake(client, (TODAY + timedelta(days=120)).isoformat())
    assert r.status_code == 201
    assert r.json()["success"] is True
    assert r.json()["message"] == "Inventory item processed successfully"
    assert r.json()["data"]["status"] == "ACCEPTED"
    assert r.json()["data"]["remaining_days"] > 60


# ── Test 2: PRIORITY_SALE ─────────────────────────────────────

def test_intake_45_days_returns_priority_sale(client):
    _create_product(client)
    r = _intake(client, (TODAY + timedelta(days=45)).isoformat())
    assert r.status_code == 201
    assert r.json()["data"]["status"] == "PRIORITY_SALE"
    assert r.json()["data"]["remaining_days"] == 45


# ── Test 3: REJECTED ─────────────────────────────────────────

def test_intake_10_days_returns_rejected(client):
    _create_product(client)
    r = _intake(client, (TODAY + timedelta(days=10)).isoformat())
    assert r.json()["data"]["status"] == "REJECTED"
    assert r.json()["data"]["remaining_days"] == 10


def test_intake_expired_returns_rejected(client):
    _create_product(client)
    assert _intake(client, (TODAY - timedelta(days=1)).isoformat()).json()["data"]["status"] == "REJECTED"


# ── Test 4: INVALID_DATE ──────────────────────────────────────

def test_intake_expiry_before_mfg_returns_invalid_date(client):
    _create_product(client)
    r = _intake(client, expiry_date="2026-01-01", manufacturing_date="2026-06-01")
    assert r.json()["data"]["status"] == "INVALID_DATE"


# ── Test 5: MANUAL_REVIEW ─────────────────────────────────────

def test_intake_missing_expiry_returns_manual_review(client):
    _create_product(client)
    r = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-NE",
        "manufacturing_date": "2026-01-01",
    })
    assert r.status_code == 201
    assert r.json()["data"]["status"] == "MANUAL_REVIEW"
    assert r.json()["data"]["remaining_days"] is None


# ── 404 on unknown barcode ────────────────────────────────────

def test_intake_unknown_barcode_returns_404(client):
    r = client.post(_i("/intake"), json={"barcode": "0000000000000", "batch_number": "B"})
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "PRODUCT_NOT_FOUND"


# ── GET /inventory ────────────────────────────────────────────

def test_list_inventory_returns_total_and_items(client):
    _create_product(client)
    _intake(client, (TODAY + timedelta(days=120)).isoformat())
    _intake(client, (TODAY + timedelta(days=45)).isoformat())
    r = client.get(_i())
    assert r.json()["data"]["total"] == 2
    assert len(r.json()["data"]["items"]) == 2


def test_list_inventory_message(client):
    assert client.get(_i()).json()["message"] == "Inventory items fetched successfully"


# ── GET /inventory/{id} ───────────────────────────────────────

def test_get_inventory_by_id(client):
    _create_product(client)
    item_id = _intake(client, (TODAY + timedelta(days=90)).isoformat()).json()["data"]["id"]
    r = client.get(_i(f"/{item_id}"))
    assert r.status_code == 200
    assert r.json()["data"]["id"] == item_id
    assert r.json()["message"] == "Inventory item fetched successfully"


def test_get_inventory_not_found(client):
    r = client.get(_i("/9999"))
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "INVENTORY_ITEM_NOT_FOUND"


# ── GET /inventory/status/{status} ───────────────────────────

def test_status_filter_accepted(client):
    _create_product(client)
    _intake(client, (TODAY + timedelta(days=120)).isoformat())
    _intake(client, (TODAY + timedelta(days=45)).isoformat())
    r = client.get(_i("/status/ACCEPTED"))
    assert r.json()["data"]["total"] == 1
    assert all(i["status"] == "ACCEPTED" for i in r.json()["data"]["items"])


def test_status_filter_priority_sale(client):
    _create_product(client)
    _intake(client, (TODAY + timedelta(days=45)).isoformat())
    assert client.get(_i("/status/PRIORITY_SALE")).json()["data"]["total"] == 1


def test_status_filter_rejected(client):
    _create_product(client)
    _intake(client, (TODAY - timedelta(days=5)).isoformat())
    assert client.get(_i("/status/REJECTED")).json()["data"]["total"] == 1


def test_status_filter_case_insensitive(client):
    _create_product(client)
    _intake(client, (TODAY + timedelta(days=120)).isoformat())
    assert client.get(_i("/status/accepted")).json()["data"]["total"] == 1


def test_status_filter_invalid_returns_400(client):
    r = client.get(_i("/status/BOGUS"))
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_STATUS"


def test_status_route_no_collision_with_id(client):
    _create_product(client)
    _intake(client, (TODAY + timedelta(days=120)).isoformat())
    assert client.get(_i("/status/ACCEPTED")).status_code != 422
