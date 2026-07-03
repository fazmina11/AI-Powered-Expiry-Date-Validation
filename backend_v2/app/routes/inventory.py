from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from typing import Any, Optional
from pydantic import BaseModel
import json
from app.models.audit_log import AuditLog
from app.models.ocr_result import OCRResult

from app.database import get_db
from app.models.inventory import InventoryItem

router = APIRouter()

def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

def _inventory_to_dict(item: InventoryItem, remaining_days: Optional[int] = None) -> dict:
    if remaining_days is None and item.expiry_date:
        remaining_days = (item.expiry_date - date.today()).days
    return {
        "id": str(item.id),
        "product_id": str(item.product_id),
        "batch_number": item.batch_number,
        "manufacturing_date": item.manufacturing_date.isoformat() if item.manufacturing_date else None,
        "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
        "remaining_days": remaining_days,
        "status": item.operator_decision or item.intake_status or "PENDING",
        "decision_reason": item.notes or item.status_reason,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }

class InventoryIntakeRequest(BaseModel):
    product_id: UUID
    barcode_scan_id: Optional[UUID] = None
    ocr_result_id: Optional[UUID] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str = "ACCEPTED"

@router.post("/intake", status_code=201)
def intake_inventory(payload: InventoryIntakeRequest, db: Session = Depends(get_db)):
    item = InventoryItem(
        product_id=payload.product_id,
        barcode_scan_id=payload.barcode_scan_id,
        ocr_result_id=payload.ocr_result_id,
        batch_number=payload.batch_number,
        manufacturing_date=payload.manufacturing_date,
        expiry_date=payload.expiry_date,
        operator_decision=payload.status,
        intake_status=payload.status,
        pipeline_status="OCR_COMPLETED" if payload.ocr_result_id else "MANUAL"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    if payload.ocr_result_id:
        ocr_res = db.query(OCRResult).filter(OCRResult.id == payload.ocr_result_id).first()
        if ocr_res:
            ocr_res.inventory_item_id = item.id
            db.commit()

    audit_log = AuditLog(
        event_type="inventory.intake",
        entity_type="inventory_item",
        entity_id=str(item.id),
        action="intake",
        message="Inventory item created manually via Save.",
        metadata_json=payload.model_dump(mode="json")
    )
    db.add(audit_log)
    db.commit()
    
    return success_response(_inventory_to_dict(item), "Inventory created successfully")

@router.get("/")
def list_inventory(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    total = db.query(InventoryItem).count()
    items = db.query(InventoryItem).offset(skip).limit(limit).all()
    data = {
        "total": total,
        "items": [_inventory_to_dict(i) for i in items]
    }
    return success_response(data, "Inventory fetched successfully")

@router.get("/{item_id}")
def get_inventory_item(item_id: UUID, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return success_response(_inventory_to_dict(item), "Inventory item fetched successfully")

from app.models.product import Product
from datetime import datetime

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_products = db.query(Product).count()
    total_inventory = db.query(InventoryItem).count()

    today = date.today()
    expiring_soon = 0
    expired = 0
    accepted = 0
    rejected = 0
    manual_review = 0

    items = db.query(InventoryItem).all()
    for item in items:
        decision = (item.operator_decision or item.intake_status or "").upper()
        if decision == "ACCEPTED":
            accepted += 1
        elif decision == "REJECTED":
            rejected += 1
        elif decision in ("MANUAL_REVIEW", "DATA_INCOMPLETE"):
            manual_review += 1

        if item.expiry_date:
            days = (item.expiry_date - today).days
            if days < 0:
                expired += 1
            elif days <= 30:
                expiring_soon += 1

    validated_today = db.query(InventoryItem).filter(
        InventoryItem.created_at >= datetime.combine(today, datetime.min.time())
    ).count()

    return success_response({
        "total_products": total_products,
        "total_inventory": total_inventory,
        "expiring_soon": expiring_soon,
        "expired": expired,
        "accepted": accepted,
        "rejected": rejected,
        "manual_review": manual_review,
        "validated_today": validated_today,
    }, "Stats fetched successfully")
