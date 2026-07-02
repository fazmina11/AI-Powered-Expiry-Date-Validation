from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.validation import ValidationRecord
from app.models.inventory import InventoryItem
from app.schemas.validation import ValidationManualCreate, ValidationResponse
from app.utils.response import success_response, error_response

router = APIRouter()


@router.post("/manual", status_code=status.HTTP_201_CREATED)
def create_manual_validation(
    data: ValidationManualCreate, db: Session = Depends(get_db)
):
    inventory_item = db.query(InventoryItem).filter(InventoryItem.id == data.inventory_item_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Inventory item not found", "INVENTORY_ITEM_NOT_FOUND"),
        )

    record = ValidationRecord(
        inventory_item_id=data.inventory_item_id,
        extracted_mfg_date=data.extracted_mfg_date,
        extracted_expiry_date=data.extracted_expiry_date,
        failure_reason=data.failure_reason,
        validation_status="manual",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return success_response(ValidationResponse.model_validate(record))


@router.get("/{inventory_item_id}")
def get_validation_records(
    inventory_item_id: int, db: Session = Depends(get_db)
):
    records = db.query(ValidationRecord).filter(
        ValidationRecord.inventory_item_id == inventory_item_id
    ).all()
    return success_response([ValidationResponse.model_validate(r) for r in records])
