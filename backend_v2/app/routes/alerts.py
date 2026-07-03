from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.scan_alert import ScanAlert
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.ocr_result import OCRResult

router = APIRouter()

def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

@router.get("/summary")
def get_alerts_summary(db: Session = Depends(get_db)):
    today = date.today()
    today_datetime = datetime.combine(today, datetime.min.time())
    
    total = db.query(ScanAlert).count()
    critical = db.query(ScanAlert).filter(ScanAlert.severity == "CRITICAL", ScanAlert.is_resolved == False).count()
    warnings = db.query(ScanAlert).filter(ScanAlert.severity == "WARNING", ScanAlert.is_resolved == False).count()
    resolved = db.query(ScanAlert).filter(ScanAlert.is_resolved == True).count()
    resolved_today = db.query(ScanAlert).filter(
        ScanAlert.is_resolved == True,
        ScanAlert.resolved_at >= today_datetime
    ).count()

    ocr_failed = db.query(ScanAlert).filter(ScanAlert.alert_type == "OCR_FAILED", ScanAlert.is_resolved == False).count()
    missing_exp = db.query(ScanAlert).filter(ScanAlert.alert_type == "MISSING_EXPIRY", ScanAlert.is_resolved == False).count()
    unknown_barcode = db.query(ScanAlert).filter(ScanAlert.alert_type == "UNKNOWN_BARCODE", ScanAlert.is_resolved == False).count()

    # We will get pending reviews from ManualReview
    from app.models.manual_review import ManualReview
    pending_reviews = db.query(ManualReview).filter(ManualReview.review_status == "PENDING").count()

    return success_response({
        "total_alerts": total,
        "critical_alerts": critical,
        "warnings": warnings,
        "resolved_alerts": resolved,
        "resolved_today": resolved_today,
        "ocr_failed": ocr_failed,
        "missing_exp": missing_exp,
        "unknown_barcode": unknown_barcode,
        "pending_reviews": pending_reviews
    }, "Summary fetched successfully")


@router.get("")
def list_alerts(
    skip: int = 0, 
    limit: int = 50,
    status: Optional[str] = Query(None, description="resolved or unresolved"),
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ScanAlert, InventoryItem, Product).outerjoin(
        InventoryItem, ScanAlert.inventory_item_id == InventoryItem.id
    ).outerjoin(
        Product, InventoryItem.product_id == Product.id
    )

    if status == "resolved":
        query = query.filter(ScanAlert.is_resolved == True)
    elif status == "unresolved":
        query = query.filter(ScanAlert.is_resolved == False)

    if severity:
        query = query.filter(ScanAlert.severity == severity)
        
    if alert_type:
        query = query.filter(ScanAlert.alert_type == alert_type)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.barcode.ilike(search_term)) |
            (InventoryItem.batch_number.ilike(search_term)) |
            (ScanAlert.alert_type.ilike(search_term))
        )

    query = query.order_by(ScanAlert.created_at.desc())
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()

    alerts_list = []
    for alert, inventory, product in results:
        alerts_list.append({
            "id": str(alert.id),
            "scan_session_id": str(alert.scan_session_id) if alert.scan_session_id else None,
            "inventory_item_id": str(alert.inventory_item_id) if alert.inventory_item_id else None,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "issue": alert.field_name or alert.alert_type,
            "is_resolved": alert.is_resolved,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "product_name": product.name if product else "Unknown",
            "barcode": product.barcode if product else "Unknown"
        })

    return success_response({"total": total, "alerts": alerts_list}, "Alerts fetched successfully")


@router.get("/{alert_id}")
def get_alert_details(alert_id: UUID, db: Session = Depends(get_db)):
    result = db.query(ScanAlert, InventoryItem, Product).outerjoin(
        InventoryItem, ScanAlert.inventory_item_id == InventoryItem.id
    ).outerjoin(
        Product, InventoryItem.product_id == Product.id
    ).filter(ScanAlert.id == alert_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert, inventory, product = result
    
    ocr_raw_text = None
    detected_mfg = None
    detected_exp = None
    detected_batch = None
    image_url = None
    
    if inventory and inventory.ocr_result_id:
        ocr_res = db.query(OCRResult).filter(OCRResult.id == inventory.ocr_result_id).first()
        if ocr_res:
            ocr_raw_text = ocr_res.raw_text
            detected_mfg = ocr_res.candidate_mfg_date.isoformat() if ocr_res.candidate_mfg_date else None
            detected_exp = ocr_res.candidate_expiry_date.isoformat() if ocr_res.candidate_expiry_date else None
            detected_batch = ocr_res.batch_number_detected
            
            from app.models.product_image import ProductImage
            img = db.query(ProductImage).filter(ProductImage.id == ocr_res.product_image_id).first()
            if img:
                image_url = img.file_url or f"/static/uploads/{img.file_path}"

    data = {
        "id": str(alert.id),
        "scan_session_id": str(alert.scan_session_id) if alert.scan_session_id else None,
        "product_name": product.name if product else "Unknown",
        "barcode": product.barcode if product else "Unknown",
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "error_reason": alert.message,
        "is_resolved": alert.is_resolved,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "ocr_raw_text": ocr_raw_text,
        "detected_mfg": detected_mfg,
        "detected_exp": detected_exp,
        "detected_batch": detected_batch,
        "image_url": image_url
    }
    
    return success_response(data, "Alert details fetched successfully")


class ResolveAlertRequest(BaseModel):
    notes: Optional[str] = None

@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: UUID, payload: Optional[ResolveAlertRequest] = None, db: Session = Depends(get_db)):
    alert = db.query(ScanAlert).filter(ScanAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_resolved = True
    alert.resolved_at = datetime.now()
    if payload and payload.notes:
        alert.resolved_by = payload.notes
        
    db.commit()
    return success_response({"id": str(alert.id), "is_resolved": True}, "Alert resolved successfully")
