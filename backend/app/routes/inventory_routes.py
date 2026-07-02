"""
routes/inventory_routes.py — Inventory Intake API endpoints.

Phase 1.5 canonical router.

Route registration order is critical:
  Static paths (/intake, /status/{status}) must be registered
  BEFORE dynamic path (/{id}) to prevent FastAPI matching
  string slugs as integers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.inventory_schema import (
    InventoryIntakeRequest,
    InventoryListResponse,
    InventoryResponse,
)
from app.services.inventory_service import (
    create_inventory_item,
    get_all_inventory,
    get_inventory_by_id,
    get_inventory_by_status,
)
from app.utils.constants import DECISION_STATUSES
from app.utils.exceptions import InventoryItemNotFoundError, ProductNotFoundError
from app.utils.response import error_response, success_response

router = APIRouter()


# ── POST /inventory/intake ────────────────────────────────────

@router.post("/intake", status_code=status.HTTP_201_CREATED)
def intake_endpoint(payload: InventoryIntakeRequest, db: Session = Depends(get_db)):
    """
    Run the full inventory intake workflow.

    Finds the product by barcode, evaluates shelf life,
    persists the InventoryItem, and returns the decision.
    """
    try:
        item = create_inventory_item(db, payload)
        return success_response(
            data=InventoryResponse.model_validate(item),
            message="Inventory item processed successfully",
        )
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(
                "No product found for this barcode", "PRODUCT_NOT_FOUND"
            ),
        )


# ── GET /inventory ────────────────────────────────────────────

@router.get("")
def list_inventory_endpoint(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """Return a paginated list of all inventory items."""
    total, items = get_all_inventory(db, skip=skip, limit=limit)
    return success_response(
        data=InventoryListResponse(
            total=total,
            items=[InventoryResponse.model_validate(i) for i in items],
        ),
        message="Inventory items fetched successfully",
    )


# ── GET /inventory/status/{status} ────────────────────────────
# IMPORTANT: registered BEFORE /{id} to avoid integer-cast errors.

@router.get("/status/{item_status}")
def get_by_status_endpoint(
    item_status: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """
    Filter inventory items by decision status.

    Supported values: ACCEPTED, PRIORITY_SALE, REJECTED, MANUAL_REVIEW, INVALID_DATE
    """
    upper_status = item_status.upper()
    if upper_status not in DECISION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                f"Invalid status '{item_status}'. "
                f"Valid values: {', '.join(sorted(DECISION_STATUSES))}",
                "INVALID_STATUS",
            ),
        )
    total, items = get_inventory_by_status(db, upper_status, skip=skip, limit=limit)
    return success_response(
        data=InventoryListResponse(
            total=total,
            items=[InventoryResponse.model_validate(i) for i in items],
        ),
        message=f"Inventory items with status '{upper_status}' fetched successfully",
    )


# ── GET /inventory/{id} ───────────────────────────────────────

@router.get("/{item_id}")
def get_inventory_item_endpoint(item_id: int, db: Session = Depends(get_db)):
    """Get a single inventory item by ID."""
    try:
        item = get_inventory_by_id(db, item_id)
        return success_response(
            data=InventoryResponse.model_validate(item),
            message="Inventory item fetched successfully",
        )
    except InventoryItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Inventory item not found", "INVENTORY_ITEM_NOT_FOUND"),
        )
