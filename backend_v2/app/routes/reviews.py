from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.manual_review import ManualReview
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.ocr_result import OCRResult

router = APIRouter()

def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

@router.get("")
def list_reviews(
    skip: int = 0, 
    limit: int = 50,
    status: Optional[str] = Query(None, description="PENDING or RESOLVED"),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ManualReview, InventoryItem, Product).outerjoin(
        InventoryItem, ManualReview.inventory_item_id == InventoryItem.id
    ).outerjoin(
        Product, InventoryItem.product_id == Product.id
    )

    if status:
        query = query.filter(ManualReview.review_status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.barcode.ilike(search_term)) |
            (InventoryItem.batch_number.ilike(search_term))
        )

    query = query.order_by(ManualReview.created_at.desc())
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()

    reviews_list = []
    for review, inventory, product in results:
        reviews_list.append({
            "id": str(review.id),
            "scan_session_id": str(review.scan_session_id) if review.scan_session_id else None,
            "inventory_item_id": str(review.inventory_item_id) if review.inventory_item_id else None,
            "review_type": review.review_type,
            "review_status": review.review_status,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "product_name": product.name if product else "Unknown",
            "barcode": product.barcode if product else "Unknown",
            "batch_number": inventory.batch_number if inventory else None,
            "original_mfg_date": review.original_mfg_date.isoformat() if review.original_mfg_date else None,
            "original_expiry_date": review.original_expiry_date.isoformat() if review.original_expiry_date else None,
            "corrected_mfg_date": review.corrected_mfg_date.isoformat() if review.corrected_mfg_date else None,
            "corrected_expiry_date": review.corrected_expiry_date.isoformat() if review.corrected_expiry_date else None,
            "human_decision": review.human_decision
        })

    return success_response({"total": total, "reviews": reviews_list}, "Reviews fetched successfully")


class CorrectReviewRequest(BaseModel):
    decision: str  # "APPROVE", "REJECT", "CORRECT_DATA", "RE_SCAN"
    corrected_product_name: Optional[str] = None
    corrected_mfg_date: Optional[date] = None
    corrected_expiry_date: Optional[date] = None
    corrected_batch_number: Optional[str] = None
    corrected_description: Optional[str] = None
    reviewer_note: Optional[str] = None

@router.post("/{review_id}/correct")
def correct_review(review_id: UUID, payload: CorrectReviewRequest, db: Session = Depends(get_db)):
    review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    review.human_decision = payload.decision
    review.review_status = "RESOLVED"
    review.reviewed_at = datetime.now()
    if payload.reviewer_note:
        review.reviewer_note = payload.reviewer_note
        
    if payload.decision == "CORRECT_DATA" or payload.decision == "APPROVE":
        review.corrected_mfg_date = payload.corrected_mfg_date or review.original_mfg_date
        review.corrected_expiry_date = payload.corrected_expiry_date or review.original_expiry_date
        review.corrected_batch_number = payload.corrected_batch_number
        review.corrected_description = payload.corrected_description
        
        # We also need to update the inventory and product appropriately
        if review.inventory_item_id:
            inventory = db.query(InventoryItem).filter(InventoryItem.id == review.inventory_item_id).first()
            if inventory:
                if payload.corrected_mfg_date: inventory.manufacturing_date = payload.corrected_mfg_date
                if payload.corrected_expiry_date: inventory.expiry_date = payload.corrected_expiry_date
                if payload.corrected_batch_number: inventory.batch_number = payload.corrected_batch_number
                
                # Update pipeline status if approved
                inventory.intake_status = "ACCEPTED" if payload.decision == "APPROVE" else inventory.intake_status
                inventory.pipeline_status = "MANUAL_CORRECTED"
                
                if payload.corrected_product_name:
                    product = db.query(Product).filter(Product.id == inventory.product_id).first()
                    if product:
                        product.name = payload.corrected_product_name
        
    db.commit()
    
    # Optional: Automatically resolve related alerts if an alert was generated for this review issue
    alerts = db.query(ScanAlert).filter(
        ScanAlert.inventory_item_id == review.inventory_item_id,
        ScanAlert.is_resolved == False
    ).all()
    
    for alert in alerts:
        alert.is_resolved = True
        alert.resolved_at = datetime.now()
        alert.resolved_by = "Auto-resolved via Manual Review Correction"
    
    if alerts:
        db.commit()
    
    return success_response({"id": str(review.id), "status": review.review_status}, "Review corrected and resolved successfully")
