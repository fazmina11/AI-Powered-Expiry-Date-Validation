from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from typing import Optional, Any
from pydantic import BaseModel
import os, uuid, shutil

from app.database import get_db
from app.services.scan_service import ScanService
from app.services.scan_pipeline_service import ScanPipelineService
from app.models.scan_session import ScanSession
from app.models.scan_alert import ScanAlert

router = APIRouter()

def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

class StartScanResponse(BaseModel):
    session_id: UUID

class BarcodeRequest(BaseModel):
    session_id: UUID
    barcode: str

class FinalizeRequest(BaseModel):
    session_id: UUID
    barcode: str
    image_path: str
    product_name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    packed_date: Optional[date] = None
    mrp: Optional[float] = None
    raw_text: Optional[str] = None
    confidence: Optional[float] = None

@router.post("/validate-frame")
async def validate_frame(file: UploadFile = File(...)):
    import cv2
    import numpy as np
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {"success": False, "message": "Invalid image file", "usable": False, "has_text": False}

        # Apply light preprocessing before quality checks so blur / glare
        # metrics are evaluated on the enhanced frame (same as what OCR sees)
        try:
            from app.services.paddle_ocr_service import _preprocess_for_ocr
            import tempfile
            fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            cv2.imwrite(tmp_path, frame)
            frame_enhanced = _preprocess_for_ocr(tmp_path)
            os.remove(tmp_path)
        except Exception:
            frame_enhanced = frame  # fall back to raw frame

        from app.services.date_roi_service import is_frame_usable
        usable, reason = is_frame_usable(frame_enhanced)
        if not usable:
            return {"success": True, "usable": False, "reason": reason, "has_text": False}

        # Product detection: lightweight EasyOCR scan on enhanced frame
        # Threshold is deliberately lenient so we don't miss dim/faint labels.
        try:
            from app.services.paddle_ocr_service import _get_reader
            reader = _get_reader()
            results = reader.readtext(frame_enhanced, detail=1)
            # Consider a text block meaningful if:
            #   - confidence > 0.20 (lenient — packaging ink varies a lot)
            #   - text length > 1
            meaningful = [r for r in results if r[2] > 0.20 and len(r[1].strip()) > 1]
            # At least 1 meaningful block is enough to confirm a label is present
            has_text = len(meaningful) >= 1

            if not has_text:
                return {"success": True, "usable": False, "reason": "No product label text detected", "has_text": False}
        except Exception as ocr_exc:
            import logging
            logging.getLogger(__name__).warning("validate-frame OCR check failed: %s", ocr_exc)
            # If the OCR check itself crashes, don't block the user — allow capture
            return {"success": True, "usable": True, "reason": "", "has_text": True}

        return {"success": True, "usable": True, "reason": "", "has_text": True}
    except Exception as exc:
        return {"success": False, "message": str(exc), "usable": False, "has_text": False}

@router.post("/start", status_code=201)
def start_scan(db: Session = Depends(get_db)):
    session = ScanService.start_session(db)
    return success_response({"session_id": session.id}, "Scan session started")

@router.post("/barcode")
def scan_barcode(payload: BarcodeRequest, db: Session = Depends(get_db)):
    res = ScanService.process_barcode(db, payload.session_id, payload.barcode)
    return success_response(res, "Barcode processed")

@router.post("/upload")
def upload_image(session_id: UUID = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate session
    session = db.query(ScanSession).filter(ScanSession.id == session_id).first()
    if not session or session.session_status != "STARTED":
        raise HTTPException(status_code=400, detail="Invalid session")

    os.makedirs("temp_uploads", exist_ok=True)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    saved_file_path = os.path.join("temp_uploads", filename)
    with open(saved_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Just return the path, we will insert it during Finalize
    return success_response({"image_path": saved_file_path}, "Image uploaded")

class RunOCRRequest(BaseModel):
    session_id: UUID
    image_path: str

@router.post("/run-ocr")
def run_ocr(payload: RunOCRRequest, db: Session = Depends(get_db)):
    session = db.query(ScanSession).filter(ScanSession.id == payload.session_id).first()
    if not session or session.session_status != "STARTED":
        raise HTTPException(status_code=400, detail="Invalid session")

    if not os.path.exists(payload.image_path):
        raise HTTPException(status_code=404, detail="Image not found")
        
    import cv2
    frame = cv2.imread(payload.image_path)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not read image file")
        
    pipeline = ScanPipelineService()
    result = pipeline.process_scan(frame)
    
    return success_response({
        "extracted_data": result.model_dump()
    }, "OCR completed")

@router.post("/finalize")
def finalize_scan(payload: FinalizeRequest, db: Session = Depends(get_db)):
    res = ScanService.finalize_session(db, payload.session_id, payload.model_dump())
    return success_response(res, "Scan finalized and inventory created")

@router.post("/cancel/{session_id}")
def cancel_scan(session_id: UUID, db: Session = Depends(get_db)):
    res = ScanService.cancel_session(db, session_id)
    return success_response(res, "Scan cancelled")

@router.get("/status/{session_id}")
def get_status(session_id: UUID, db: Session = Depends(get_db)):
    session = db.query(ScanSession).filter(ScanSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return success_response({"status": session.session_status}, "Status retrieved")

@router.get("/alerts/{session_id}")
def get_alerts(session_id: UUID, db: Session = Depends(get_db)):
    alerts = db.query(ScanAlert).filter(ScanAlert.scan_session_id == session_id).all()
    return success_response([{"message": a.message, "type": a.alert_type} for a in alerts], "Alerts retrieved")


# ── Async Queue worker task ──
def process_queued_scan(ocr_result_id: UUID, image_path: str, barcode: Optional[str]):
    import logging
    from datetime import datetime
    from app.database import SessionLocal
    from app.models.ocr_result import OCRResult
    from app.models.product_image import ProductImage
    from app.models.product import Product
    from app.models.inventory import InventoryItem
    from app.models.scan_alert import ScanAlert
    
    logger = logging.getLogger("scan_queue_worker")
    db = SessionLocal()
    try:
        ocr_result = db.query(OCRResult).filter(OCRResult.id == ocr_result_id).first()
        if not ocr_result:
            logger.error(f"[Worker] OCRResult {ocr_result_id} not found in database.")
            return
            
        ocr_result.ocr_status = "processing"
        db.commit()
        
        logger.info(f"[Worker] Processing scan for OCRResult {ocr_result_id}...")
        pipeline = ScanPipelineService()
        result = pipeline.process_scan(image_path)
        
        # BUILD EXTRACTION SUMMARY (human-readable, structured text)
        summary_lines = []
        if result.product and result.product.name:
            summary_lines.append(f"Product: {result.product.name}")
            if result.product.brand:
                summary_lines.append(f"Brand: {result.product.brand}")
        if result.batch and result.batch.batch_number:
            summary_lines.append(f"Batch: {result.batch.batch_number}")
        if result.manufacturing and result.manufacturing.manufacturing_date:
            summary_lines.append(f"MFG Date: {result.manufacturing.manufacturing_date}")
        if result.expiry and result.expiry.expiry_date:
            summary_lines.append(f"Expiry Date: {result.expiry.expiry_date}")
        if result.pricing and result.pricing.price:
            summary_lines.append(f"MRP: ₹{result.pricing.price}")
        if result.product and result.product.weight:
            summary_lines.append(f"Weight: {result.product.weight}")
        if result.product and result.product.ingredients:
            summary_lines.append(f"Ingredients: {result.product.ingredients}")
            
        # Store the summary as raw_text (this is what the frontend displays)
        ocr_result.raw_text = "\n".join(summary_lines) if summary_lines else (result.ocr.raw_text if result.ocr else "")
        
        # Store overall confidence from OCR
        if result.ocr:
            ocr_result.overall_confidence = result.ocr.confidence
            
        # Map ProductIntelligence fields → OCRResult database columns
        if result.manufacturing and result.manufacturing.manufacturing_date:
            ocr_result.candidate_mfg_date = result.manufacturing.manufacturing_date
        if result.expiry and result.expiry.expiry_date:
            ocr_result.candidate_expiry_date = result.expiry.expiry_date
        if result.batch:
            ocr_result.batch_number_detected = result.batch.batch_number
        if result.pricing and result.pricing.price is not None:
            try:
                mrp_val = str(result.pricing.price).replace(',', '')
                ocr_result.mrp_detected = float(mrp_val)
            except (ValueError, TypeError):
                ocr_result.mrp_detected = result.pricing.price
            
        if result.product:
            ocr_result.extracted_product_name = result.product.name
            ocr_result.extracted_brand = result.product.brand
            ocr_result.extracted_description = result.product.category
            ocr_result.extracted_ingredients_text = result.product.ingredients
            
        # Store bounding boxes (ocr_blocks) → extracted_text_blocks column
        if hasattr(result, 'ocr_blocks') and result.ocr_blocks:
            ocr_result.extracted_text_blocks = result.ocr_blocks
            
        # Try to resolve barcode and product
        barcode_val = barcode or (result.barcode.value if result.barcode else None)
        product = None
        if barcode_val:
            product = db.query(Product).filter(Product.barcode == barcode_val).first()
            if product:
                ocr_result.product_id = product.id
                
        # Handle auto-saving to inventory if validation succeeded
        if result.status == "SUCCESS" and product:
            try:
                # 1. BarcodeScan
                from app.models.barcode_scan import BarcodeScan
                b_scan = BarcodeScan(
                    raw_barcode=barcode_val,
                    scan_session_id=ocr_result.scan_session_id,
                    product_id=product.id,
                    scan_status="success"
                )
                db.add(b_scan)
                db.flush()
                
                # 2. InventoryItem
                inv_item = InventoryItem(
                    product_id=product.id,
                    barcode_scan_id=b_scan.id,
                    scan_session_id=ocr_result.scan_session_id,
                    ocr_result_id=ocr_result.id,
                    batch_number=ocr_result.batch_number_detected,
                    manufacturing_date=ocr_result.candidate_mfg_date,
                    expiry_date=ocr_result.candidate_expiry_date,
                    pipeline_status="OCR_COMPLETED",
                    intake_status="COMPLETED"
                )
                db.add(inv_item)
                db.flush()
                
                ocr_result.inventory_item_id = inv_item.id
                
                # 3. AuditLog
                from app.models.audit_log import AuditLog
                audit = AuditLog(
                    event_type="inventory.intake",
                    entity_type="inventory_item",
                    entity_id=str(inv_item.id),
                    action="intake_finalize",
                    message="Inventory item automatically created via async queue."
                )
                db.add(audit)
            except Exception as inner_e:
                logger.error(f"[Worker] Failed auto-saving inventory item: {inner_e}")
                
        # Generate Alerts
        if result.alerts and result.alerts.alerts:
            for alert_msg in result.alerts.alerts:
                # Extract fields safely from the validation Alert schema object
                code = getattr(alert_msg, 'code', 'VALIDATION_ERROR')
                sev = getattr(alert_msg, 'severity', 'HIGH')
                msg = getattr(alert_msg, 'message', str(alert_msg))
                
                db.add(ScanAlert(
                    scan_session_id=ocr_result.scan_session_id,
                    alert_type=code,
                    severity=sev,
                    message=msg
                ))
                
        ocr_result.ocr_status = "completed" if (result.ocr or result.status in ["SUCCESS", "PARTIAL_SUCCESS"]) else "failed"
        if result.status == "FAILED_QUALITY":
            ocr_result.failure_reason = result.reject_reason or "Quality check failed"
            ocr_result.ocr_status = "failed"
            
        ocr_result.processed_at = datetime.utcnow()
        db.commit()
        logger.info(f"[Worker] Completed background scan {ocr_result_id}. status={ocr_result.ocr_status}")
    except Exception as exc:
        db.rollback()
        logger.error(f"[Worker] Failed background scan task: {exc}", exc_info=True)
        try:
            db2 = SessionLocal()
            ocr_result = db2.query(OCRResult).filter(OCRResult.id == ocr_result_id).first()
            if ocr_result:
                ocr_result.ocr_status = "failed"
                ocr_result.failure_reason = str(exc)
                db2.commit()
            db2.close()
        except:
            pass
    finally:
        db.close()


@router.post("/enqueue")
def enqueue_scan(
    file: UploadFile = File(...),
    session_id: Optional[UUID] = Form(None),
    barcode: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    from app.models.scan_session import ScanSession
    from app.models.product_image import ProductImage
    from app.models.ocr_result import OCRResult
    from app.models.product import Product
    
    # 1. Resolve or create ScanSession
    session = None
    if session_id:
        session = db.query(ScanSession).filter(ScanSession.id == session_id).first()
    if not session:
        session = db.query(ScanSession).filter(ScanSession.session_status == "STARTED").first()
    if not session:
        session = ScanSession(session_status="STARTED", operator_name="AutoScan Queue")
        db.add(session)
        db.flush()
        
    # 2. Save uploaded file to uploads directory and preprocess for OCR
    os.makedirs("uploads", exist_ok=True)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    saved_file_path = os.path.join("uploads", filename)
    with open(saved_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Preprocess the saved image (upscale, glare removal, CLAHE, sharpening)
    # This replaces the raw capture with an OCR-optimised version on disk
    try:
        import cv2
        from app.services.paddle_ocr_service import _preprocess_for_ocr
        enhanced_frame = _preprocess_for_ocr(saved_file_path)
        # Save preprocessed image back, overwriting the raw capture
        cv2.imwrite(saved_file_path, enhanced_frame)
    except Exception as pre_exc:
        import logging
        logging.getLogger("scan_enqueue").warning(
            "[Enqueue] Image preprocessing failed, keeping raw capture: %s", pre_exc
        )
        
    # 3. Create placeholder product if barcode present and does not exist
    product_id = None
    if barcode:
        prod = db.query(Product).filter(Product.barcode == barcode).first()
        if not prod:
            placeholder_id = str(uuid.uuid4())
            prod = Product(
                name="Pending OCR Scan",
                barcode=barcode,
                sku=f"SKU-{placeholder_id}"
            )
            db.add(prod)
            db.flush()
        product_id = prod.id
    else:
        # Create a unique placeholder product to prevent ForeignKey violation
        placeholder_id = str(uuid.uuid4())
        prod = Product(
            name="Pending OCR Scan",
            barcode=f"PENDING-{placeholder_id}",
            sku=f"SKU-{placeholder_id}"
        )
        db.add(prod)
        db.flush()
        product_id = prod.id
            
    # 4. Create ProductImage
    p_image = ProductImage(
        scan_session_id=session.id,
        file_path=saved_file_path,
        product_id=product_id,
        processing_status="pending"
    )
    db.add(p_image)
    db.flush()
    
    # 5. Create OCRResult
    ocr_result = OCRResult(
        scan_session_id=session.id,
        product_image_id=p_image.id,
        product_id=product_id,
        ocr_status="pending"
    )
    db.add(ocr_result)
    db.commit()
    db.refresh(ocr_result)
    
    # 6. Run asynchronous task
    if background_tasks:
        background_tasks.add_task(process_queued_scan, ocr_result.id, saved_file_path, barcode)
        
    return success_response({
        "ocr_result_id": str(ocr_result.id),
        "session_id": str(session.id),
        "status": "pending",
        "image_path": saved_file_path
    }, "Scan enqueued successfully")


@router.get("/history")
def get_scan_history(db: Session = Depends(get_db)):
    from app.models.ocr_result import OCRResult
    from app.models.product_image import ProductImage
    from app.models.product import Product
    
    # Get recent scan tasks
    results = db.query(OCRResult).order_by(OCRResult.created_at.desc()).limit(20).all()
    
    data = []
    for r in results:
        img_url = None
        if r.product_image and r.product_image.file_path:
            basename = os.path.basename(r.product_image.file_path)
            img_url = f"/static/uploads/{basename}"
            
        data.append({
            "id": str(r.id),
            "session_id": str(r.scan_session_id) if r.scan_session_id else None,
            "status": r.ocr_status,
            "failure_reason": r.failure_reason,
            "image_url": img_url,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "product": {
                # Prefer OCR-extracted name over the placeholder product row name
                "name": r.extracted_product_name or (
                    r.product.name if r.product and not r.product.name.startswith("Pending OCR") else None
                ) or "Unknown Product",
                "brand": r.extracted_brand or (r.product.brand if r.product else None),
                "barcode": r.product.barcode if r.product and not r.product.barcode.startswith("PENDING-") else None,
            },
            "extracted_data": {
                "manufacturing_date": r.candidate_mfg_date.isoformat() if r.candidate_mfg_date else None,
                "expiry_date": r.candidate_expiry_date.isoformat() if r.candidate_expiry_date else None,
                "batch_number": r.batch_number_detected,
                "mrp": float(r.mrp_detected) if r.mrp_detected else None,
                "raw_text": r.raw_text,
                "confidence": float(r.overall_confidence) if r.overall_confidence else 0.0,
                # Include extra fields the frontend modal can use
                "product_name": r.extracted_product_name,
                "brand": r.extracted_brand,
                "ingredients": r.extracted_ingredients_text,
            },
            "ocr_blocks": r.extracted_text_blocks
        })
    return success_response(data, "Scan history retrieved")


@router.delete("/clear-history")
def clear_scan_history(db: Session = Depends(get_db)):
    from app.models.ocr_result import OCRResult
    from app.models.product_image import ProductImage
    from app.models.scan_alert import ScanAlert
    
    try:
        # Delete all scan alerts first (FK dependency)
        db.query(ScanAlert).delete()
        # Delete all OCR results
        db.query(OCRResult).delete()
        # Delete all product images
        db.query(ProductImage).delete()
        db.commit()
        
        # Also clean up upload files on disk
        import glob
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "uploads")
        for f in glob.glob(os.path.join(upload_dir, "*")):
            if os.path.isfile(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        
        return success_response(None, "All scan history cleared")
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/result/{result_id}")
def get_ocr_result_status(result_id: UUID, db: Session = Depends(get_db)):
    from app.models.ocr_result import OCRResult
    from app.models.product import Product
    
    r = db.query(OCRResult).filter(OCRResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="OCR Result not found")
        
    img_url = None
    if r.product_image and r.product_image.file_path:
        basename = os.path.basename(r.product_image.file_path)
        img_url = f"/static/uploads/{basename}"
        
    return success_response({
        "id": str(r.id),
        "session_id": str(r.scan_session_id) if r.scan_session_id else None,
        "status": r.ocr_status,
        "failure_reason": r.failure_reason,
        "image_url": img_url,
        "product": {
            "name": r.extracted_product_name or (
                r.product.name if r.product and not r.product.name.startswith("Pending OCR") else None
            ) or "Unknown Product",
            "brand": r.extracted_brand or (r.product.brand if r.product else None),
            "barcode": r.product.barcode if r.product and not r.product.barcode.startswith("PENDING-") else None,
        },
        "extracted_data": {
            "manufacturing_date": r.candidate_mfg_date.isoformat() if r.candidate_mfg_date else None,
            "expiry_date": r.candidate_expiry_date.isoformat() if r.candidate_expiry_date else None,
            "batch_number": r.batch_number_detected,
            "mrp": float(r.mrp_detected) if r.mrp_detected else None,
            "raw_text": r.raw_text,
            "confidence": float(r.overall_confidence) if r.overall_confidence else 0.0,
            # Extra fields for the review modal
            "product_name": r.extracted_product_name,
            "brand": r.extracted_brand,
            "ingredients": r.extracted_ingredients_text,
        },
        "ocr_blocks": r.extracted_text_blocks
    }, "OCR status retrieved")
