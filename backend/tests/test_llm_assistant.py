"""
tests/test_llm_assistant.py — Integration and mock verification tests for Phase 6 LLM Assistant.
"""

from unittest.mock import patch, MagicMock
from tests.conftest import API, MILK_PRODUCT


def _p(path=""):
    return f"{API}/products{path}"


def _fp(path=""):
    return f"{API}/financial-profiles{path}"


def _i(path=""):
    return f"{API}/inventory{path}"


def _a(path=""):
    return f"{API}/assistant{path}"


@patch("app.services.llm_assistant.provider.HuggingFaceProvider.generate_response")
def test_assistant_chat_success(mock_generate, client):
    mock_generate.return_value = "This batch was redistributed because there is high demand in Mumbai."

    # Seed warehouse configurations
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    import scripts.generate_warehouse_intelligence as gen
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

    # Create inventory item
    item_id = client.post(_i("/intake"), json={
        "barcode": "8901234567890",
        "batch_number": "BATCH-CHAT",
        "quantity": 100,
        "expiry_date": "2026-12-01"
    }).json()["data"]["id"]

    # Trigger chat request
    payload = {
        "inventory_item_id": item_id,
        "question": "Why was this batch redistributed?",
        "conversation_history": [
            {"role": "user", "content": "Hello assistant."},
            {"role": "assistant", "content": "Hello! I am here to help you."}
        ]
    }
    r = client.post(_a("/chat"), json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "This batch was redistributed" in data["answer"]
    assert data["model"] == "meta-llama/Llama-3.2-3B-Instruct"
    assert data["sources"] == ["Financial Decision Engine", "Warehouse Intelligence", "Cost Benefit Optimizer"]
    assert data["prompt_version"] == "1.0"


@patch("app.services.llm_assistant.provider.HuggingFaceProvider.generate_response")
def test_assistant_executive_summary_success(mock_generate, client):
    mock_generate.return_value = "The warehouse contains 5 high-risk batches."

    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    import scripts.generate_warehouse_intelligence as gen
    with patch("scripts.generate_warehouse_intelligence.SessionLocal", return_value=db):
        gen.main()

    # Trigger GET /assistant/executive-summary
    r = client.get(_a("/executive-summary?warehouse=WH-BLR&category=Dairy&priority=HIGH"))
    assert r.status_code == 200
    data = r.json()
    assert "The warehouse contains" in data["summary"]
    assert data["model"] == "meta-llama/Llama-3.2-3B-Instruct"
    assert data["prompt_version"] == "1.0"

