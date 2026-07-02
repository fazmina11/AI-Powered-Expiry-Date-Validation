"""
tests/test_dashboard.py — Phase 1.7 dashboard endpoint tests.
Routes live under /api/v1/dashboard
"""

from datetime import date, timedelta

from tests.conftest import API, MILK_PRODUCT

TODAY = date.today()


def _p(path=""):
    return f"{API}/products{path}"


def _i(path=""):
    return f"{API}/inventory{path}"


def _v(path=""):
    return f"{API}/validation{path}"


def _d(path=""):
    return f"{API}/dashboard{path}"


def _setup_product(client):
    client.post(_p(), json=MILK_PRODUCT)


def _intake(client, expiry_date=None, manufacturing_date="2026-01-01"):
    payload = {"barcode": "8901234567890", "batch_number": "B"}
    if manufacturing_date:
        payload["manufacturing_date"] = manufacturing_date
    if expiry_date:
        payload["expiry_date"] = expiry_date
    return client.post(_i("/intake"), json=payload)


def _full_setup(client):
    """Insert one item of each status."""
    _setup_product(client)
    _intake(client, (TODAY + timedelta(days=120)).isoformat())          # ACCEPTED
    _intake(client, (TODAY + timedelta(days=45)).isoformat())           # PRIORITY_SALE
    _intake(client, (TODAY - timedelta(days=5)).isoformat())            # REJECTED
    _intake(client)                                                       # MANUAL_REVIEW
    _intake(client, expiry_date="2026-01-01", manufacturing_date="2026-06-01")  # INVALID_DATE


# ── GET /dashboard/summary ────────────────────────────────────

def test_dashboard_summary_empty_db(client):
    r = client.get(_d("/summary"))
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total_products"] == 0
    assert data["total_inventory_items"] == 0
    assert data["accepted_count"] == 0
    assert data["priority_sale_count"] == 0
    assert data["rejected_count"] == 0
    assert data["manual_review_count"] == 0
    assert data["invalid_date_count"] == 0
    assert data["valid_validation_count"] == 0
    assert data["low_confidence_count"] == 0


def test_dashboard_summary_counts(client):
    _full_setup(client)
    r = client.get(_d("/summary"))
    assert r.status_code == 200
    assert r.json()["message"] == "Dashboard summary retrieved"
    data = r.json()["data"]
    assert data["total_products"] == 1
    assert data["total_inventory_items"] == 5
    assert data["accepted_count"] == 1
    assert data["priority_sale_count"] == 1
    assert data["rejected_count"] == 1
    assert data["manual_review_count"] == 1
    assert data["invalid_date_count"] == 1


def test_dashboard_summary_includes_validation_counts(client):
    _full_setup(client)
    # Add one VALID and one LOW_CONFIDENCE validation record
    item_id = _intake(client, (TODAY + timedelta(days=90)).isoformat()).json()["data"]["id"]
    client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.95,
    })
    client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.50,
    })
    data = client.get(_d("/summary")).json()["data"]
    assert data["valid_validation_count"] == 1
    assert data["low_confidence_count"] == 1


# ── GET /dashboard/inventory-breakdown ───────────────────────

def test_inventory_breakdown(client):
    _full_setup(client)
    r = client.get(_d("/inventory-breakdown"))
    assert r.status_code == 200
    assert r.json()["message"] == "Inventory breakdown retrieved"
    data = r.json()["data"]
    assert data["accepted"] == 1
    assert data["priority_sale"] == 1
    assert data["rejected"] == 1
    assert data["manual_review"] == 1
    assert data["invalid_date"] == 1


def test_inventory_breakdown_empty(client):
    data = client.get(_d("/inventory-breakdown")).json()["data"]
    assert all(v == 0 for v in data.values())


# ── GET /dashboard/validation-breakdown ──────────────────────

def test_validation_breakdown(client):
    _setup_product(client)
    item_id = _intake(client, (TODAY + timedelta(days=90)).isoformat()).json()["data"]["id"]
    client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.95,   # VALID
    })
    client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "confidence_score": 0.50,   # LOW_CONFIDENCE — but missing expiry → MANUAL_REVIEW
    })
    r = client.get(_d("/validation-breakdown"))
    assert r.status_code == 200
    assert r.json()["message"] == "Validation breakdown retrieved"
    data = r.json()["data"]
    assert data["valid"] == 1
    assert "low_confidence" in data
    assert "manual_review" in data


# ── GET /dashboard/recent-inventory ──────────────────────────

def test_recent_inventory_default_limit(client):
    _setup_product(client)
    for _ in range(5):
        _intake(client, (TODAY + timedelta(days=90)).isoformat())
    r = client.get(_d("/recent-inventory"))
    assert r.status_code == 200
    assert r.json()["message"] == "Recent inventory retrieved"
    assert len(r.json()["data"]) == 5


def test_recent_inventory_custom_limit(client):
    _setup_product(client)
    for _ in range(5):
        _intake(client, (TODAY + timedelta(days=90)).isoformat())
    r = client.get(_d("/recent-inventory?limit=3"))
    assert len(r.json()["data"]) == 3


def test_recent_inventory_empty(client):
    r = client.get(_d("/recent-inventory"))
    assert r.status_code == 200
    assert r.json()["data"] == []


# ── GET /dashboard/recent-validations ────────────────────────

def test_recent_validations(client):
    _setup_product(client)
    item_id = _intake(client, (TODAY + timedelta(days=90)).isoformat()).json()["data"]["id"]
    for score in [0.95, 0.80, 0.60]:
        client.post(_v("/manual"), json={
            "inventory_item_id": item_id,
            "extracted_expiry_date": "2026-11-01",
            "confidence_score": score,
        })
    r = client.get(_d("/recent-validations"))
    assert r.status_code == 200
    assert r.json()["message"] == "Recent validations retrieved"
    assert len(r.json()["data"]) == 3


def test_recent_validations_custom_limit(client):
    _setup_product(client)
    item_id = _intake(client, (TODAY + timedelta(days=90)).isoformat()).json()["data"]["id"]
    for score in [0.95, 0.80, 0.60, 0.50]:
        client.post(_v("/manual"), json={
            "inventory_item_id": item_id,
            "extracted_expiry_date": "2026-11-01",
            "confidence_score": score,
        })
    assert len(client.get(_d("/recent-validations?limit=2")).json()["data"]) == 2


# ── GET /dashboard/alerts ─────────────────────────────────────

def test_alerts_returns_problematic_items(client):
    _full_setup(client)
    r = client.get(_d("/alerts"))
    assert r.status_code == 200
    assert r.json()["message"] == "Alerts retrieved"
    data = r.json()["data"]
    # REJECTED + INVALID_DATE + MANUAL_REVIEW = 3 alert items
    assert data["count"] == 3
    statuses = {item["status"] for item in data["items"]}
    assert "REJECTED" in statuses
    assert "INVALID_DATE" in statuses
    assert "MANUAL_REVIEW" in statuses
    # ACCEPTED and PRIORITY_SALE must NOT appear
    assert "ACCEPTED" not in statuses
    assert "PRIORITY_SALE" not in statuses


def test_alerts_empty_when_all_accepted(client):
    _setup_product(client)
    _intake(client, (TODAY + timedelta(days=120)).isoformat())  # ACCEPTED
    data = client.get(_d("/alerts")).json()["data"]
    assert data["count"] == 0
    assert data["items"] == []


def test_alerts_count_matches_items_length(client):
    _full_setup(client)
    data = client.get(_d("/alerts")).json()["data"]
    assert data["count"] == len(data["items"])
