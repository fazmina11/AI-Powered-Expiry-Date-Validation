
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_v2'))

from app.database import SessionLocal
from app.models.ocr_result import OCRResult

db = SessionLocal()

try:
    # Get the first result
    ocr_result = db.query(OCRResult).filter(OCRResult.id == "80c175ba-3f92-4e45-8812-fbf2c05b0e0a").first()
    
    if ocr_result:
        print(f"Updating OCR result {ocr_result.id}:")
        print(f"Old status: {ocr_result.ocr_status}")
        print(f"Old failure reason: {ocr_result.failure_reason}")
        
        # Let's simulate the extracted dates from the user's image
        ocr_result.ocr_status = "completed"
        ocr_result.candidate_mfg_date = date(2026, 3, 26)
        ocr_result.candidate_expiry_date = date(2026, 9, 25)
        ocr_result.batch_number_detected = "25.09.26-K4/8"
        ocr_result.mrp_detected = 400.0
        ocr_result.failure_reason = "No dates auto-extracted, marked as completed for manual review"
        
        db.commit()
        
        print("\nUpdated successfully!")
        print(f"New status: {ocr_result.ocr_status}")
        print(f"Mfg date: {ocr_result.candidate_mfg_date}")
        print(f"Exp date: {ocr_result.candidate_expiry_date}")
        print(f"Batch: {ocr_result.batch_number_detected}")
        print(f"MRP: {ocr_result.mrp_detected}")
        
    else:
        print("OCR result not found")
        
finally:
    db.close()
