"""
tests/test_validation.py — Phase 1.6 validation record tests.
Routes live under /api/v1/validation
"""

from tests.conftest import API, MILK_PRODUCT


def _p(path=""):
    return f"{API}/products{path}"


def _i(path=""):
    return f"{API}/inventory{path}"


def _v(path=""):
    return f"{API}/validation{path}"


def _create_product_and_intake(client):
    client.post(_p(), json=MILK_PRODUCT)
    r = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH001",
        "manufacturing_date": "2026-01-01",
    })
    return r.json()["data"]["id"]


# ── Test 1: VALID ─────────────────────────────────────────────

def test_confidence_095_returns_valid(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "raw_text": "MFG 01/05/2026 EXP 01/11/2026",
        "extracted_mfg_date": "2026-05-01",
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.95,
    })
    assert r.status_code == 201
    assert r.json()["message"] == "Validation record stored"
    assert r.json()["data"]["validation_status"] == "VALID"
    assert r.json()["data"]["confidence_score"] == 0.95


def test_confidence_exactly_080_is_valid(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.80,
    })
    assert r.json()["data"]["validation_status"] == "VALID"


# ── Test 2: LOW_CONFIDENCE ────────────────────────────────────

def test_confidence_060_returns_low_confidence(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.60,
    })
    assert r.json()["data"]["validation_status"] == "LOW_CONFIDENCE"


def test_confidence_079_is_low_confidence(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.79,
    })
    assert r.json()["data"]["validation_status"] == "LOW_CONFIDENCE"


# ── Test 3: MANUAL_REVIEW ─────────────────────────────────────

def test_missing_expiry_returns_manual_review(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "confidence_score": 0.95,
    })
    assert r.json()["data"]["validation_status"] == "MANUAL_REVIEW"


def test_missing_confidence_returns_manual_review(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "extracted_expiry_date": "2026-11-01",
    })
    assert r.json()["data"]["validation_status"] == "MANUAL_REVIEW"


# ── Error cases ───────────────────────────────────────────────

def test_unknown_inventory_item_returns_404(client):
    r = client.post(_v("/manual"), json={
        "inventory_item_id": 9999,
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.95,
    })
    assert r.status_code == 404
    assert r.json()["detail"]["error_code"] == "INVENTORY_ITEM_NOT_FOUND"


def test_confidence_above_1_rejected(client):
    item_id = _create_product_and_intake(client)
    assert client.post(_v("/manual"), json={"inventory_item_id": item_id, "confidence_score": 1.5}).status_code == 422


def test_confidence_below_0_rejected(client):
    item_id = _create_product_and_intake(client)
    assert client.post(_v("/manual"), json={"inventory_item_id": item_id, "confidence_score": -0.1}).status_code == 422


# ── OCR placeholder fields ────────────────────────────────────

def test_raw_text_and_score_stored(client):
    item_id = _create_product_and_intake(client)
    r = client.post(_v("/manual"), json={
        "inventory_item_id": item_id,
        "raw_text": "MFG 01/05/2026 EXP 01/11/2026",
        "extracted_expiry_date": "2026-11-01",
        "confidence_score": 0.98,
    })
    assert r.json()["data"]["raw_text"] == "MFG 01/05/2026 EXP 01/11/2026"
    assert r.json()["data"]["confidence_score"] == 0.98


# ── GET /validation/{inventory_item_id} ───────────────────────

def test_get_validation_records(client):
    item_id = _create_product_and_intake(client)
    for score in [0.95, 0.60]:
        client.post(_v("/manual"), json={
            "inventory_item_id": item_id,
            "extracted_expiry_date": "2026-11-01",
            "confidence_score": score,
        })
    r = client.get(_v(f"/{item_id}"))
    assert r.status_code == 200
    assert r.json()["message"] == "Validation records fetched successfully"
    assert len(r.json()["data"]) == 2


def test_get_validation_records_empty(client):
    item_id = _create_product_and_intake(client)
    assert client.get(_v(f"/{item_id}")).json()["data"] == []
