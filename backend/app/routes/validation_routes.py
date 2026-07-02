"""
routes/validation_routes.py — Validation Record API endpoints.

Phase 1.6 canonical router.

Designed as the OCR integration point:
  POST /validation/manual  — OCR team pushes extracted data here
  GET  /validation/{id}    — fetch all records for an inventory item
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.validation_schema import ValidationCreate, ValidationResponse
from app.services.validation_service import (
    create_validation_record,
    get_validation_by_inventory,
)
from app.utils.exceptions import InventoryItemNotFoundError
from app.utils.response import error_response, success_response

router = APIRouter()


# ── POST /validation/manual ───────────────────────────────────

@router.post("/manual", status_code=status.HTTP_201_CREATED)
def create_validation_endpoint(payload: ValidationCreate, db: Session = Depends(get_db)):
    """
    Store a validation record for an inventory item.

    Used by warehouse staff for manual entry now.
    Will be called by the OCR pipeline in a future phase —
    the payload shape is already designed for that integration.

    validation_status is derived automatically:
      confidence >= 0.80            → VALID
      confidence < 0.80             → LOW_CONFIDENCE
      missing expiry or confidence  → MANUAL_REVIEW
    """
    try:
        record = create_validation_record(db, payload)
        return success_response(
            data=ValidationResponse.model_validate(record),
            message="Validation record stored",
        )
    except InventoryItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Inventory item not found", "INVENTORY_ITEM_NOT_FOUND"),
        )


# ── GET /validation/{inventory_item_id} ───────────────────────

@router.get("/{inventory_item_id}")
def get_validation_records_endpoint(
    inventory_item_id: int, db: Session = Depends(get_db)
):
    """
    Return all validation records for a given inventory item, newest first.
    Returns an empty list if none exist — not a 404.
    """
    records = get_validation_by_inventory(db, inventory_item_id)
    return success_response(
        data=[ValidationResponse.model_validate(r) for r in records],
        message="Validation records fetched successfully",
    )
