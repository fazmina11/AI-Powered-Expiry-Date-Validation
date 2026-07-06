"""
tests/test_financial_profile.py — Integration tests for ProductFinancialProfile CRUD and Synthetic Generator.
"""

from decimal import Decimal
from tests.conftest import MILK_PRODUCT, API


def _url(path=""):
    return f"{API}/financial-profiles{path}"


def _product_url(path=""):
    return f"{API}/products{path}"


# ── CREATE ────────────────────────────────────────────────────

def test_create_financial_profile_success(client):
    # 1. Create a product first
    r_prod = client.post(_product_url(), json=MILK_PRODUCT)
    assert r_prod.status_code == 201
    prod_id = r_prod.json()["data"]["id"]

    # 2. Create financial profile
    payload = {
        "product_id": prod_id,
        "purchase_price": "45.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "10.00",
        "currency": "INR"
    }
    r = client.post(_url(), json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["success"] is True
    assert body["data"]["product_id"] == prod_id
    assert body["data"]["purchase_price"] == "45.00"
    assert body["data"]["mrp"] == "50.00"
    assert body["data"]["currency"] == "INR"


def test_create_financial_profile_pricing_validation(client):
    # Create product
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]

    # Try creating with MRP < purchase_price (Pydantic validator will trigger 422)
    payload = {
        "product_id": prod_id,
        "purchase_price": "55.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "10.00"
    }
    r = client.post(_url(), json=payload)
    assert r.status_code == 422
    assert "MRP must be greater than or equal to purchase price" in r.text


def test_create_financial_profile_mrp_equal_purchase_price(client):
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]

    payload = {
        "product_id": prod_id,
        "purchase_price": "50.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "0.00"
    }
    r = client.post(_url(), json=payload)
    assert r.status_code == 201



def test_create_duplicate_financial_profile_rejected(client):
    # Create product
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]

    payload = {
        "product_id": prod_id,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00"
    }
    r1 = client.post(_url(), json=payload)
    assert r1.status_code == 201

    # Try duplicate
    r2 = client.post(_url(), json=payload)
    assert r2.status_code == 409
    assert r2.json()["detail"]["error_code"] == "DUPLICATE_FINANCIAL_PROFILE"


def test_create_financial_profile_product_not_found(client):
    payload = {
        "product_id": 99999,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00"
    }
    r = client.post(_url(), json=payload)
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "PRODUCT_NOT_FOUND"


# ── GET BY ID ─────────────────────────────────────────────────

def test_get_financial_profile_success(client):
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]
    payload = {
        "product_id": prod_id,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00"
    }
    client.post(_url(), json=payload)

    r = client.get(_url(f"/{prod_id}"))
    assert r.status_code == 200
    assert r.json()["data"]["mrp"] == "50.00"
    assert r.json()["data"]["purchase_price"] == "40.00"


def test_get_financial_profile_not_found(client):
    r = client.get(_url("/99999"))
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "FINANCIAL_PROFILE_NOT_FOUND"


# ── UPDATE ────────────────────────────────────────────────────

def test_update_financial_profile_success(client):
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]
    payload = {
        "product_id": prod_id,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00"
    }
    client.post(_url(), json=payload)

    # Partial update mrp
    r = client.put(_url(f"/{prod_id}"), json={"mrp": "60.00"})
    assert r.status_code == 200
    assert r.json()["data"]["mrp"] == "60.00"
    assert r.json()["data"]["purchase_price"] == "40.00"


def test_update_financial_profile_invalid_pricing(client):
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]
    payload = {
        "product_id": prod_id,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00"
    }
    client.post(_url(), json=payload)

    # Try setting mrp <= existing purchase_price (40.00)
    r = client.put(_url(f"/{prod_id}"), json={"mrp": "35.00"})
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_PRICING"


# ── DELETE CASCADING ──────────────────────────────────────────

def test_delete_product_cascades_financial_profile(client):
    prod_id = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]
    payload = {
        "product_id": prod_id,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00"
    }
    client.post(_url(), json=payload)

    # Delete product
    r_del = client.delete(_product_url(f"/{prod_id}"))
    assert r_del.status_code == 200

    # Verification: Financial profile lookup returns 404
    r_get = client.get(_url(f"/{prod_id}"))
    assert r_get.status_code == 404


# ── LIST ──────────────────────────────────────────────────────

def test_list_financial_profiles(client):
    p1 = client.post(_product_url(), json=MILK_PRODUCT).json()["data"]["id"]
    p2 = client.post(_product_url(), json={"name": "Orange Juice", "sku": "JUI-ORG", "barcode": "111"}).json()["data"]["id"]

    client.post(_url(), json={"product_id": p1, "purchase_price": "40.00", "mrp": "50.00", "default_profit_margin_percent": "20.00"})
    client.post(_url(), json={"product_id": p2, "purchase_price": "80.00", "mrp": "100.00", "default_profit_margin_percent": "20.00"})

    r = client.get(_url())
    assert r.status_code == 200
    assert len(r.json()["data"]) == 2


# ── SYNTHETIC GENERATOR ───────────────────────────────────────

def test_synthetic_generator_reproducibility(client):
    # Create products under different categories
    p1 = client.post(_product_url(), json={"name": "Amul Milk 1L", "sku": "AMUL-1L", "barcode": "890123", "category": "Dairy"}).json()["data"]["id"]
    p2 = client.post(_product_url(), json={"name": "Coca Cola 500ml", "sku": "COKE-500", "barcode": "890124", "category": "Beverages"}).json()["data"]["id"]
    p3 = client.post(_product_url(), json={"name": "Whole Wheat Bread", "sku": "BREAD-WW", "barcode": "890125", "category": "Bakery"}).json()["data"]["id"]

    # Trigger generator
    r_gen = client.post(_url("/generate-synthetic?seed=100"))
    assert r_gen.status_code == 200
    assert r_gen.json()["data"]["created_count"] == 3

    # Fetch profiles and store generated values
    prof1_first = client.get(_url(f"/{p1}")).json()["data"]
    prof2_first = client.get(_url(f"/{p2}")).json()["data"]
    prof3_first = client.get(_url(f"/{p3}")).json()["data"]

    # Verify Dairy has 12% margin
    assert float(prof1_first["default_profit_margin_percent"]) == 12.0
    # Verify Beverages has 15% margin
    assert float(prof2_first["default_profit_margin_percent"]) == 15.0
    # Verify Bakery has 20% margin
    assert float(prof3_first["default_profit_margin_percent"]) == 20.0

    # Triggering generator again should yield 0 new profiles
    r_gen_dup = client.post(_url("/generate-synthetic?seed=100"))
    assert r_gen_dup.json()["data"]["created_count"] == 0
