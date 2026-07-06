"""
tests/test_financial_decision.py — Integration tests for Phase 3 Standalone Financial Decision Engine.
"""

from decimal import Decimal
from tests.conftest import API, MILK_PRODUCT


def _p(path=""):
    return f"{API}/products{path}"


def _fp(path=""):
    return f"{API}/financial-profiles{path}"


def _i(path=""):
    return f"{API}/inventory{path}"


def test_financial_analysis_success(client):
    # 1. Create a product and a financial profile
    pid = client.post(_p(), json=MILK_PRODUCT).json()["data"]["id"]
    client.post(_fp(), json={
        "product_id": pid,
        "purchase_price": "40.00",
        "mrp": "50.00",
        "default_profit_margin_percent": "20.00",
        "supplier_return_allowed": True,
        "supplier_return_percent": "90.00"
    })

    # 2. Intake an inventory item
    item_id = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-P3",
        "quantity": 10,
        "expiry_date": "2026-10-15"
    }).json()["data"]["id"]

    # 3. Create a validation record (to add ML confidence score)
    client.post(f"{API}/validation/manual", json={
        "inventory_item_id": item_id,
        "confidence_score": 0.95
    })

    # 4. Fetch financial analysis
    r = client.get(_i(f"/{item_id}/financial-analysis"))
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]

    # Verify Calculations
    # inventory_cost = 10 * 40.00 = 400.00
    assert data["inventory_cost"] == "400.00"
    # potential_revenue = 10 * 50.00 = 500.00
    assert data["potential_revenue"] == "500.00"
    # potential_financial_loss = 0.00 (not expired)
    assert data["potential_financial_loss"] == "0.00"
    # supplier_recoverable_value = 400.00 * 90% = 360.00
    assert data["supplier_recoverable_value"] == "360.00"
    # maximum_recoverable_value = max(360.00, 500.00) = 500.00
    assert data["maximum_recoverable_value"] == "500.00"

    # Verify Health score, priority, status and decision readiness
    assert float(data["financial_health_score"]) > 0
    assert data["financial_status"] in ["EXCELLENT", "HEALTHY", "AT_RISK", "CRITICAL"]
    assert data["financial_priority"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(data["financial_explanations"], list)
    assert len(data["financial_explanations"]) > 0
    assert isinstance(data["decision_ready"], bool)


def test_financial_analysis_expired_potential_loss(client):
    pid = client.post(_p(), json=MILK_PRODUCT).json()["data"]["id"]
    client.post(_fp(), json={
        "product_id": pid,
        "purchase_price": "100.00",
        "mrp": "120.00",
        "default_profit_margin_percent": "16.67",
        "supplier_return_allowed": False
    })

    # Intake an already expired item
    item_id = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-EXP",
        "quantity": 5,
        "expiry_date": "2026-01-01" # expired
    }).json()["data"]["id"]

    r = client.get(_i(f"/{item_id}/financial-analysis"))
    assert r.status_code == 200
    data = r.json()["data"]

    # inventory_cost = 5 * 100 = 500.00
    assert data["inventory_cost"] == "500.00"
    # potential_financial_loss = total cost (500.00) because it is expired
    assert data["potential_financial_loss"] == "500.00"
    # supplier return allowed = False -> 0.00 recoverable
    assert data["supplier_recoverable_value"] == "0.00"
    # explanations check
    assert any("expired" in exp.lower() for exp in data["financial_explanations"])


def test_financial_analysis_not_found(client):
    r = client.get(_i("/99999/financial-analysis"))
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "INVENTORY_NOT_FOUND"

