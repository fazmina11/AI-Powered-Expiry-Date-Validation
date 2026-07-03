from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
import numpy as np
import logging

from app.database import get_db
from app.services.scan_pipeline_service import ScanPipelineService
from app.services.transaction_service import TransactionService

log = logging.getLogger("ocr_route")
router = APIRouter()

def success_response(data: any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

@router.post("/upload")
async def scan_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        import cv2
        contents = await file.read()
        
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        saved_file_name = f"{uuid.uuid4()}{file_ext}"
        saved_file_path = os.path.join(upload_dir, saved_file_name)
        
        with open(saved_file_path, "wb") as f:
            f.write(contents)

        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Could not decode image. Please upload a valid image file.")

        pipeline = ScanPipelineService()
        result = pipeline.process_scan(frame)
        
        db_records = TransactionService.persist_scan_pipeline_results(db, result, saved_file_path)
        
        response_data = result.model_dump()
        response_data["db_records"] = db_records

        return success_response(response_data, "Image scanned and persisted successfully")
    except HTTPException:
        raise
    except Exception as exc:
        log.error("scan_image error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan pipeline error: {str(exc)}")
