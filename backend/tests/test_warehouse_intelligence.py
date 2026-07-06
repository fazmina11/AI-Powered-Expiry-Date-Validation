"""
tests/test_warehouse_intelligence.py — Integration and validation tests for Phase 4 Warehouse Intelligence Layer.
"""

from decimal import Decimal
from tests.conftest import API
from app.database import SessionLocal
from scripts.generate_warehouse_intelligence import main as run_generation_script


def _w(path=""):
    return f"{API}/warehouse-intelligence{path}"


def test_warehouse_intelligence_generation_and_apis(client):
    # 1. Execute the generator script main logic bound to the test engine
    # In conftest, client override overrides get_db, but the script runs with SessionLocal.
    # To run it correctly against the client's database, we override the sessionmaker used in the script,
    # OR we can simply call the API routes (the tables will be created automatically by metadata on test client setup).
    # Wait, let's trigger the generator's main logic by passing the client's session, or we can just trigger it!
    # Let's inspect the script. It imports SessionLocal from app.database.
    # In pytest, app.database SessionLocal can be patched or overridden, but since conftest does:
    # `fastapi_app.dependency_overrides[get_db] = override_get_db`,
    # the endpoints will see the override. For direct database operations in the test, we can use the db session.
    # Let's check how we can seed. Let's obtain a database session from fastapi dependency overrides:
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())


    # Run the generator logic against the test DB
    import scripts.generate_warehouse_intelligence as gen
    # Directly execute generation on the test db session
    gen.db = db
    # We patch the db inside gen to use the test db session
    from unittest.mock import patch
    with patch("scripts.generate_warehouse_intelligence.SessionLocal", return_value=db):
        run_generation_script()

    # 2. Verify Database Counts
    from app.models.warehouse import Warehouse, WarehouseConfiguration, WarehouseDemandProfile, WarehouseTransferMatrix, SupplierReturnPolicy
    
    assert db.query(Warehouse).count() == 10
    assert db.query(WarehouseConfiguration).count() == 10
    assert db.query(WarehouseDemandProfile).count() == 50  # 10 * 5 categories
    assert db.query(WarehouseTransferMatrix).count() == 90  # 10 * 9 routes
    assert db.query(SupplierReturnPolicy).count() == 8

    # 3. Test GET /warehouse-intelligence/demand
    r_dem = client.get(_w("/demand"))
    assert r_dem.status_code == 200
    dem_data = r_dem.json()["data"]
    assert len(dem_data) > 0
    # Verify average_sell_through_days is present
    assert "average_sell_through_days" in dem_data[0]
    assert float(dem_data[0]["average_daily_demand"]) > 0

    # Test filtering by warehouse
    r_dem_filt = client.get(_w("/demand?warehouse=WH-BLR"))
    assert len(r_dem_filt.json()["data"]) == 5  # 5 categories for BLR

    # Test filtering by category
    r_dem_cat = client.get(_w("/demand?category=Dairy"))
    assert len(r_dem_cat.json()["data"]) == 10  # 10 warehouses

    # 4. Test GET /warehouse-intelligence/transfer-matrix
    r_mat = client.get(_w("/transfer-matrix"))
    assert r_mat.status_code == 200
    mat_data = r_mat.json()["data"]
    assert len(mat_data) == 50  # default page limit
    assert float(mat_data[0]["distance_km"]) > 0
    assert float(mat_data[0]["total_transfer_cost"]) > 0
    assert mat_data[0]["road_condition_factor"] in ["GOOD", "MODERATE", "POOR"]
    # Ensure no self-transfer exists
    assert all(m["source_warehouse_id"] != m["destination_warehouse_id"] for m in mat_data)

    # Test source filtering
    r_mat_src = client.get(_w("/transfer-matrix?source_warehouse=WH-BLR"))
    assert len(r_mat_src.json()["data"]) == 9  # transfers to 9 other warehouses

    # 5. Test GET /warehouse-intelligence/supplier-policies
    r_pol = client.get(_w("/supplier-policies"))
    assert r_pol.status_code == 200
    pol_data = r_pol.json()["data"]
    assert len(pol_data) == 8
    assert "minimum_return_quantity" in pol_data[0]
    assert "maximum_return_quantity" in pol_data[0]

    # Test supplier filtering
    r_pol_filt = client.get(_w("/supplier-policies?supplier=Amul"))
    assert len(r_pol_filt.json()["data"]) == 1
    assert r_pol_filt.json()["data"][0]["supplier_id"] == "Amul"

    # 6. Test GET /warehouse-intelligence/configuration
    r_cfg = client.get(_w("/configuration"))
    assert r_cfg.status_code == 200
    cfg_data = r_cfg.json()["data"]
    assert len(cfg_data) == 10

    # Test configuration filtering
    r_cfg_filt = client.get(_w("/configuration?warehouse=WH-MUM"))
    assert len(r_cfg_filt.json()["data"]) == 1
    assert r_cfg_filt.json()["data"][0]["warehouse_id"] == "WH-MUM"
    assert r_cfg_filt.json()["data"][0]["priority_level"] == "HIGH"
