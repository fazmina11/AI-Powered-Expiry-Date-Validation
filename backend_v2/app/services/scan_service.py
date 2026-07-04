import uuid
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.scan_session import ScanSession
from app.models.scan_alert import ScanAlert
from app.models.barcode_scan import BarcodeScan
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.ocr_result import OCRResult
from app.models.inventory import InventoryItem
from app.models.audit_log import AuditLog

log = logging.getLogger("scan_service")

class ScanService:
    @staticmethod
    def start_session(db: Session, operator_name: str = "System"):
        active = db.query(ScanSession).filter(ScanSession.session_status == "STARTED").first()
        if active:
            return active
            
        session = ScanSession(session_status="STARTED", operator_name=operator_name)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
        
    @staticmethod
    def cancel_session(db: Session, session_id: uuid.UUID):
        session = db.query(ScanSession).filter(ScanSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session.session_status = "CANCELLED"
        session.completed_at = datetime.utcnow()
        db.commit()
        return {"message": "Session cancelled"}

    @staticmethod
    def process_barcode(db: Session, session_id: uuid.UUID, barcode: str):
        session = db.query(ScanSession).filter(ScanSession.id == session_id).first()
        if not session or session.session_status != "STARTED":
            raise HTTPException(status_code=400, detail="Invalid or inactive session")
            
        product = db.query(Product).filter(Product.barcode == barcode).first()
        
        # Do not insert into DB yet. Just return the lookup result.
        return {
            "product_found": bool(product),
            "product": product
        }

    @staticmethod
    def finalize_session(db: Session, session_id: uuid.UUID, payload: dict):
        session = db.query(ScanSession).filter(ScanSession.id == session_id).first()
        if not session or session.session_status != "STARTED":
            raise HTTPException(status_code=400, detail="Invalid or inactive session")
            
        # STEP 6: Validation (Validating payloads before the massive transaction)
        alerts = []
        if not payload.get("barcode"):
            alerts.append("Barcode missing")
        if not payload.get("image_path"):
            alerts.append("Image Missing")
        if not payload.get("expiry_date"):
            alerts.append("Missing Expiry Date")
            
        if alerts:
            # If validation fails, create scan_alerts and reject
            for alert_msg in alerts:
                db.add(ScanAlert(
                    scan_session_id=session.id,
                    alert_type="VALIDATION_ERROR",
                    severity="HIGH",
                    message=alert_msg
                ))
            db.commit()
            raise HTTPException(status_code=400, detail={"message": "Validation failed", "alerts": alerts})
            
        # STEP 5: ONE Database Transaction
        try:
            # 1. Barcode Scan
            product = db.query(Product).filter(Product.barcode == payload.get("barcode")).first()
            b_scan = BarcodeScan(
                raw_barcode=payload.get("barcode"),
                scan_session_id=session.id,
                product_id=product.id if product else None,
                scan_status="success" if product else "not_found"
            )
            db.add(b_scan)
            db.flush() # flush to get b_scan.id

            # 2. Product Image
            # Check if one exists
            p_image = db.query(ProductImage).filter(ProductImage.scan_session_id == session.id).first()
            if not p_image:
                p_image = ProductImage(
                    scan_session_id=session.id,
                    image_url=payload.get("image_path"),
                    file_path=payload.get("image_path"),
                    file_size_bytes=1024, # Mock size
                    mime_type="image/jpeg"
                )
                db.add(p_image)
                db.flush()

            # 3. OCR Result
            # Update existing if available
            ocr_res = db.query(OCRResult).filter(OCRResult.scan_session_id == session.id).first()
            if not ocr_res:
                ocr_res = OCRResult(
                    scan_session_id=session.id,
                    product_image_id=p_image.id,
                    raw_text=payload.get("raw_text"),
                    ocr_confidence=payload.get("confidence"),
                    extracted_product_name=payload.get("product_name"),
                    extracted_brand=payload.get("brand"),
                    extracted_description=payload.get("description"),
                    candidate_mfg_date=payload.get("manufacturing_date"),
                    candidate_expiry_date=payload.get("expiry_date"),
                    batch_number_detected=payload.get("batch_number"),
                    mrp_detected=payload.get("mrp"),
                    candidate_packed_date=payload.get("packed_date"),
                    ocr_status="completed"
                )
                db.add(ocr_res)
            else:
                ocr_res.raw_text = payload.get("raw_text") or ocr_res.raw_text
                ocr_res.candidate_mfg_date = payload.get("manufacturing_date") or ocr_res.candidate_mfg_date
                ocr_res.candidate_expiry_date = payload.get("expiry_date") or ocr_res.candidate_expiry_date
                ocr_res.batch_number_detected = payload.get("batch_number") or ocr_res.batch_number_detected
                ocr_res.mrp_detected = payload.get("mrp") or ocr_res.mrp_detected
                ocr_res.ocr_status = "completed"
            
            db.flush()

            # 4. Inventory Item
            if not product:
                # If no product, we must abort inventory creation to avoid constraint violation
                raise ValueError("Product not found in database. Manual creation required.")

            inv_item = InventoryItem(
                product_id=product.id,
                barcode_scan_id=b_scan.id,
                scan_session_id=session.id,
                ocr_result_id=ocr_res.id,
                batch_number=payload.get("batch_number"),
                manufacturing_date=payload.get("manufacturing_date"),
                expiry_date=payload.get("expiry_date"),
                packed_date=payload.get("packed_date"),
                pipeline_status="OCR_COMPLETED",
                intake_status="COMPLETED"
            )
            db.add(inv_item)
            db.flush()

            # 5. Audit Log
            audit = AuditLog(
                event_type="inventory.intake",
                entity_type="inventory_item",
                entity_id=str(inv_item.id),
                action="intake_finalize",
                message="Inventory item created via stateful scan flow."
            )
            db.add(audit)

            # Link back OCR result to inventory item
            ocr_res.inventory_item_id = inv_item.id
            
            # Mark Session Completed
            session.session_status = "COMPLETED"
            session.completed_at = datetime.utcnow()
            
            # COMMIT EVERYTHING AT ONCE
            db.commit()
            
            return {"message": "Inventory successfully created", "inventory_id": inv_item.id}
            
        except Exception as e:
            db.rollback()
            db.add(ScanAlert(
                scan_session_id=session.id,
                alert_type="SYSTEM_ERROR",
                severity="CRITICAL",
                message=f"Database Error: {str(e)}"
            ))
            db.commit()
            raise HTTPException(status_code=500, detail=str(e))
