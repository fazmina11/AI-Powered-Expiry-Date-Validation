"""
services/validation_service.py — ValidationRecord management.

Business logic for Phase 1.6.  No OCR or ML here.

Validation status rules:
  confidence_score >= 0.80            → VALID
  confidence_score < 0.80             → LOW_CONFIDENCE
  extracted_expiry_date is None       → MANUAL_REVIEW
  confidence_score is None (manual)   → MANUAL_REVIEW

The OCR team will POST to /validation/manual with their extracted data.
This service persists the record and derives validation_status from the
confidence score so warehouse staff know which records need human review.
"""

from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.validation_record import ValidationRecord
from app.schemas.validation_schema import ValidationCreate
from app.utils.constants import MANUAL_REVIEW, VALID, LOW_CONFIDENCE
from app.utils.exceptions import InventoryItemNotFoundError

# Threshold from the Phase 1.6 spec
CONFIDENCE_THRESHOLD = 0.80


def _derive_validation_status(data: ValidationCreate) -> str:
    """
    Derive validation_status from the submitted data.

    Priority:
      1. No expiry date extracted → MANUAL_REVIEW (can't validate without it)
      2. No confidence score (manual entry) → MANUAL_REVIEW
      3. Score >= threshold → VALID
      4. Score < threshold  → LOW_CONFIDENCE
    """
    if data.extracted_expiry_date is None:
        return MANUAL_REVIEW
    if data.confidence_score is None:
        return MANUAL_REVIEW
    return VALID if data.confidence_score >= CONFIDENCE_THRESHOLD else LOW_CONFIDENCE


def create_validation_record(db: Session, data: ValidationCreate) -> ValidationRecord:
    """
    Persist a new ValidationRecord.

    Raises:
        InventoryItemNotFoundError — if the referenced InventoryItem does not exist.
    """
    # Verify the inventory item exists
    item = db.query(InventoryItem).filter(InventoryItem.id == data.inventory_item_id).first()
    if not item:
        raise InventoryItemNotFoundError(
            f"Inventory item {data.inventory_item_id} not found"
        )

    validation_status = _derive_validation_status(data)

    record = ValidationRecord(
        inventory_item_id=data.inventory_item_id,
        raw_text=data.raw_text,
        extracted_mfg_date=data.extracted_mfg_date,
        extracted_expiry_date=data.extracted_expiry_date,
        confidence_score=data.confidence_score,
        validation_status=validation_status,
        failure_reason=None,   # set by manual override if needed
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_validation_by_inventory(
    db: Session, inventory_item_id: int
) -> list[ValidationRecord]:
    """
    Return all ValidationRecords for a given InventoryItem, newest first.
    """
    return (
        db.query(ValidationRecord)
        .filter(ValidationRecord.inventory_item_id == inventory_item_id)
        .order_by(ValidationRecord.created_at.desc())
        .all()
    )
