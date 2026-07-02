"""
tests/test_products.py — Phase 1.3 product API tests.
Routes live under /api/v1/products
"""

from tests.conftest import MILK_PRODUCT, API


def _url(path=""):
    return f"{API}/products{path}"


# ── CREATE ────────────────────────────────────────────────────

def test_create_product_success(client):
    r = client.post(_url(), json=MILK_PRODUCT)
    assert r.status_code == 201
    body = r.json()
    assert body["success"] is True
    assert body["message"] == "Product created successfully"
    assert body["data"]["sku"] == "MILK-500ML"
    assert body["data"]["barcode"] == "8901234567890"
    assert body["data"]["id"] is not None


def test_create_product_returns_timestamps(client):
    r = client.post(_url(), json=MILK_PRODUCT)
    data = r.json()["data"]
    assert "created_at" in data
    assert "updated_at" in data


def test_duplicate_barcode_rejected(client):
    client.post(_url(), json=MILK_PRODUCT)
    r = client.post(_url(), json={**MILK_PRODUCT, "sku": "MILK-V2"})
    assert r.status_code == 409
    assert r.json()["detail"]["error_code"] == "DUPLICATE_BARCODE"


def test_duplicate_sku_rejected(client):
    client.post(_url(), json=MILK_PRODUCT)
    r = client.post(_url(), json={**MILK_PRODUCT, "barcode": "9999999999999"})
    assert r.status_code == 409
    assert r.json()["detail"]["error_code"] == "DUPLICATE_SKU"


def test_create_product_without_optional_fields(client):
    r = client.post(_url(), json={"name": "Generic", "sku": "GEN-001", "barcode": "1234567890001"})
    assert r.status_code == 201
    assert r.json()["data"]["category"] is None
    assert r.json()["data"]["image_url"] is None


# ── BARCODE LOOKUP ────────────────────────────────────────────

def test_barcode_lookup_found(client):
    client.post(_url(), json=MILK_PRODUCT)
    r = client.get(_url("/barcode/8901234567890"))
    assert r.status_code == 200
    assert r.json()["message"] == "Product fetched successfully"
    assert r.json()["data"]["sku"] == "MILK-500ML"


def test_barcode_lookup_not_found(client):
    r = client.get(_url("/barcode/0000000000000"))
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "PRODUCT_NOT_FOUND"


def test_barcode_route_no_collision(client):
    r = client.get(_url("/barcode/8901234567890"))
    assert r.status_code != 422


# ── GET BY ID ─────────────────────────────────────────────────

def test_get_product_by_id(client):
    pid = client.post(_url(), json=MILK_PRODUCT).json()["data"]["id"]
    r = client.get(_url(f"/{pid}"))
    assert r.status_code == 200
    assert r.json()["data"]["id"] == pid


def test_get_product_not_found(client):
    r = client.get(_url("/9999"))
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "PRODUCT_NOT_FOUND"


# ── LIST ──────────────────────────────────────────────────────

def test_list_products_empty(client):
    r = client.get(_url())
    assert r.status_code == 200
    assert r.json()["data"] == []


def test_list_products_returns_all(client):
    client.post(_url(), json=MILK_PRODUCT)
    client.post(_url(), json={"name": "Juice", "sku": "JUI-001", "barcode": "1111111111111"})
    assert len(client.get(_url()).json()["data"]) == 2


def test_list_products_message(client):
    assert client.get(_url()).json()["message"] == "Products fetched successfully"


# ── UPDATE ────────────────────────────────────────────────────

def test_update_product_category(client):
    pid = client.post(_url(), json=MILK_PRODUCT).json()["data"]["id"]
    r = client.put(_url(f"/{pid}"), json={"category": "Beverages"})
    assert r.status_code == 200
    assert r.json()["message"] == "Product updated successfully"
    assert r.json()["data"]["category"] == "Beverages"


def test_update_product_sku(client):
    pid = client.post(_url(), json=MILK_PRODUCT).json()["data"]["id"]
    r = client.put(_url(f"/{pid}"), json={"sku": "MILK-1L"})
    assert r.json()["data"]["sku"] == "MILK-1L"


def test_update_duplicate_sku_rejected(client):
    client.post(_url(), json=MILK_PRODUCT)
    p2 = client.post(_url(), json={"name": "Juice", "sku": "JUI-001", "barcode": "111"}).json()["data"]["id"]
    r = client.put(_url(f"/{p2}"), json={"sku": "MILK-500ML"})
    assert r.status_code == 409
    assert r.json()["detail"]["error_code"] == "DUPLICATE_SKU"


def test_update_product_not_found(client):
    assert client.put(_url("/9999"), json={"category": "X"}).status_code == 404


# ── DELETE ────────────────────────────────────────────────────

def test_delete_product_success(client):
    pid = client.post(_url(), json=MILK_PRODUCT).json()["data"]["id"]
    r = client.delete(_url(f"/{pid}"))
    assert r.status_code == 200
    assert r.json()["message"] == "Product deleted successfully"


def test_delete_product_no_longer_retrievable(client):
    pid = client.post(_url(), json=MILK_PRODUCT).json()["data"]["id"]
    client.delete(_url(f"/{pid}"))
    assert client.get(_url(f"/{pid}")).status_code == 404


def test_delete_product_not_found(client):
    r = client.delete(_url("/9999"))
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "PRODUCT_NOT_FOUND"
