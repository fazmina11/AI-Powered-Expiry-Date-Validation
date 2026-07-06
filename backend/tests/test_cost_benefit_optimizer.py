"""
tests/test_cost_benefit_optimizer.py — Integration tests for Phase 5 Cost-Benefit Optimization Engine.
"""

from decimal import Decimal
from tests.conftest import API, MILK_PRODUCT


def _p(path=""):
    return f"{API}/products{path}"


def _fp(path=""):
    return f"{API}/financial-profiles{path}"


def _i(path=""):
    return f"{API}/inventory{path}"


def test_cost_benefit_optimization_redistribute_success(client):
    # Seeding warehouse intelligence to make sure routes exist
    # Obtain session and seed DB
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    
    import scripts.generate_warehouse_intelligence as gen
    from unittest.mock import patch
    with patch("scripts.generate_warehouse_intelligence.SessionLocal", return_value=db):
        gen.main()

    # Create product and profile
    pid = client.post(_p(), json=MILK_PRODUCT).json()["data"]["id"]
    client.post(_fp(), json={
        "product_id": pid,
        "purchase_price": "40.00",
        "mrp": "55.00",
        "default_profit_margin_percent": "27.27",
        "supplier_return_allowed": False
    })

    # Create a fresh item with high quantity and shelf life
    # High quantity makes redistribution yield high potential revenue, making it win
    item_id = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-REDIST",
        "quantity": 100,
        "expiry_date": "2026-12-01"
    }).json()["data"]["id"]

    r = client.get(_i(f"/{item_id}/optimization"))
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]

    # Verify Response Fields
    assert data["recommended_action"] == "REDISTRIBUTE"
    assert data["destination_warehouse_id"] is not None
    assert data["destination_warehouse_name"] is not None
    assert len(data["recommendation_ranking"]) == 3
    assert data["recommendation_ranking"][0]["action"] == "REDISTRIBUTE"
    assert float(data["recommendation_confidence"]) > 0
    assert "roi_percent" in data
    assert len(data["recommendation_explanation"]) > 0
    assert data["decision_engine_version"] == "1.0"


def test_cost_benefit_optimization_return_to_supplier(client):
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    
    import scripts.generate_warehouse_intelligence as gen
    from unittest.mock import patch
    with patch("scripts.generate_warehouse_intelligence.SessionLocal", return_value=db):
        gen.main()

    prod_payload = {
        "name": "Amul Milk Packet",
        "sku": "Amul-MILK-500ML",
        "barcode": "8901234567890",
        "category": "Dairy",
    }
    pid = client.post(_p(), json=prod_payload).json()["data"]["id"]
    client.post(_fp(), json={
        "product_id": pid,
        "purchase_price": "100.00",
        "mrp": "120.00",
        "default_profit_margin_percent": "16.67",
        "supplier_return_allowed": True,
        "supplier_return_percent": "95.00"
    })

    # Intake an item that is getting close to expiry (10 days remaining)
    # Supplier policy allows returns with window 3 days, shelf-life 5.
    # 10 days exceeds minimum shelf life, but makes redistribution risky, so return to supplier wins

    item_id = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-SUPPRETURN",
        "quantity": 50,
        "expiry_date": "2026-07-15"
    }).json()["data"]["id"]

    r = client.get(_i(f"/{item_id}/optimization"))
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["recommended_action"] == "RETURN_TO_SUPPLIER"
    assert data["destination_warehouse_id"] is None
    # ROI must be 0 because transport_cost is 0 for local return to supplier
    assert data["transport_cost"] == "0.00"
    assert data["roi_percent"] == "0.00"


def test_cost_benefit_optimization_dispose(client):
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    
    import scripts.generate_warehouse_intelligence as gen
    from unittest.mock import patch
    with patch("scripts.generate_warehouse_intelligence.SessionLocal", return_value=db):
        gen.main()

    pid = client.post(_p(), json=MILK_PRODUCT).json()["data"]["id"]
    client.post(_fp(), json={
        "product_id": pid,
        "purchase_price": "10.00",
        "mrp": "15.00",
        "default_profit_margin_percent": "33.33",
        "supplier_return_allowed": False
    })

    # Expired item with no return allowed and very small value -> should recommend DISPOSE
    item_id = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-DISPOSE",
        "quantity": 2,
        "expiry_date": "2026-01-01"
    }).json()["data"]["id"]

    r = client.get(_i(f"/{item_id}/optimization"))
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["recommended_action"] == "DISPOSE"
    assert data["destination_warehouse_id"] is None
    assert data["transport_cost"] == "0.00"
    assert data["roi_percent"] == "0.00"
