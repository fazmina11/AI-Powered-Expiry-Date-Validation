from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.scan_alert import ScanAlert
from app.models.manual_review import ManualReview

router = APIRouter()

def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

class ReviewResolveRequest(BaseModel):
    decision: str
    notes: Optional[str] = None

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(ScanAlert).order_by(ScanAlert.created_at.desc()).all()
    
    alert_list = []
    for a in alerts:
        product_name = "Unknown"
        if a.inventory_item and a.inventory_item.product:
            product_name = a.inventory_item.product.name
            
        alert_list.append({
            "id": str(a.id),
            "inventory_item_id": str(a.inventory_item_id) if a.inventory_item_id else None,
            "product_name": product_name,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "is_resolved": a.is_resolved,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None
        })
        
    return success_response({"alerts": alert_list}, "Alerts fetched successfully")


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: UUID, db: Session = Depends(get_db)):
    alert = db.query(ScanAlert).filter(ScanAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return success_response({"id": str(alert.id), "is_resolved": True}, "Alert resolved successfully")


@router.get("/reviews")
def get_reviews(db: Session = Depends(get_db)):
    reviews = db.query(ManualReview).order_by(ManualReview.created_at.desc()).all()
    
    review_list = []
    for r in reviews:
        product_name = "Unknown"
        if r.inventory_item and r.inventory_item.product:
            product_name = r.inventory_item.product.name
            
        review_list.append({
            "id": str(r.id),
            "inventory_item_id": str(r.inventory_item_id) if r.inventory_item_id else None,
            "product_name": product_name,
            "review_type": r.review_type,
            "review_status": r.review_status,
            "human_decision": r.human_decision,
            "review_notes": r.review_notes,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
        
    return success_response({"reviews": review_list}, "Reviews fetched successfully")


@router.post("/reviews/{review_id}/resolve")
def resolve_review(review_id: UUID, payload: ReviewResolveRequest, db: Session = Depends(get_db)):
    review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    review.human_decision = payload.decision
    review.review_notes = payload.notes
    review.review_status = "resolved"
    review.reviewed_at = datetime.utcnow()
    
    if review.inventory_item:
        review.inventory_item.intake_status = payload.decision
        review.inventory_item.operator_decision = payload.decision
        if payload.notes:
            review.inventory_item.notes = payload.notes
            
    db.commit()
    
    return success_response({"id": str(review.id), "status": review.review_status}, "Review resolved successfully")
