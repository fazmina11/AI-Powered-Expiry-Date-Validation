"""
routes/warehouse_routes.py — REST API routes for Warehouse Intelligence Layer.
Mounted under /api/v1/warehouse-intelligence.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.warehouse_schema import (
    WarehouseDemandProfileResponse,
    WarehouseTransferMatrixResponse,
    SupplierReturnPolicyResponse,
    WarehouseConfigurationResponse,
)
from app.services.warehouse_intelligence.warehouse_demand_service import list_demand_profiles
from app.services.warehouse_intelligence.transfer_cost_service import list_transfer_matrix
from app.services.warehouse_intelligence.supplier_return_service import list_supplier_policies
from app.services.warehouse_intelligence.warehouse_config_service import list_configurations
from app.utils.response import success_response

router = APIRouter()


# ── GET /warehouse-intelligence/demand ───────────────────────────

@router.get("/demand")
def get_warehouse_demand_endpoint(
    warehouse_id: Optional[str] = Query(default=None, alias="warehouse"),
    category: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve category-level product demand profiles, optionally filtered by warehouse or category."""
    profiles = list_demand_profiles(
        db,
        warehouse_id=warehouse_id,
        category=category,
        skip=skip,
        limit=limit,
    )
    return success_response(
        data=[WarehouseDemandProfileResponse.model_validate(p) for p in profiles],
        message="Warehouse demand profiles retrieved successfully",
    )


# ── GET /warehouse-intelligence/transfer-matrix ──────────────────

@router.get("/transfer-matrix")
def get_warehouse_transfer_matrix_endpoint(
    source_warehouse_id: Optional[str] = Query(default=None, alias="source_warehouse"),
    destination_warehouse_id: Optional[str] = Query(default=None, alias="destination_warehouse"),
    warehouse_id: Optional[str] = Query(default=None, alias="warehouse"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve transfer cost matrix records between warehouses, with optional origin/destination filters."""
    matrix = list_transfer_matrix(
        db,
        warehouse_id=warehouse_id,
        source_warehouse_id=source_warehouse_id,
        destination_warehouse_id=destination_warehouse_id,
        skip=skip,
        limit=limit,
    )
    return success_response(
        data=[WarehouseTransferMatrixResponse.model_validate(m) for m in matrix],
        message="Warehouse transfer cost matrix retrieved successfully",
    )


# ── GET /warehouse-intelligence/supplier-policies ────────────────

@router.get("/supplier-policies")
def get_supplier_policies_endpoint(
    supplier_id: Optional[str] = Query(default=None, alias="supplier"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve supplier return policies, optionally filtered by supplier name/ID."""
    policies = list_supplier_policies(
        db,
        supplier_id=supplier_id,
        skip=skip,
        limit=limit,
    )
    return success_response(
        data=[SupplierReturnPolicyResponse.model_validate(p) for p in policies],
        message="Supplier return policies retrieved successfully",
    )


# ── GET /warehouse-intelligence/configuration ────────────────────

@router.get("/configuration")
def get_warehouse_configuration_endpoint(
    warehouse_id: Optional[str] = Query(default=None, alias="warehouse"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve operational configs and dispatch priorities for warehouses."""
    configs = list_configurations(
        db,
        warehouse_id=warehouse_id,
        skip=skip,
        limit=limit,
    )
    return success_response(
        data=[WarehouseConfigurationResponse.model_validate(c) for c in configs],
        message="Warehouse configurations retrieved successfully",
    )
