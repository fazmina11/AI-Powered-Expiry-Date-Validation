
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_v2'))

from app.database import SessionLocal
from app.models.ocr_result import OCRResult
from datetime import datetime

db = SessionLocal()

try:
    results = db.query(OCRResult).order_by(OCRResult.created_at.desc()).limit(10).all()
    print(f"Found {len(results)} OCR results:")
    for r in results:
        print(f"\nID: {r.id}")
        print(f"Status: {r.ocr_status}")
        print(f"Created at: {r.created_at}")
        print(f"Mfg date: {r.candidate_mfg_date}")
        print(f"Expiry date: {r.candidate_expiry_date}")
        print(f"Batch: {r.batch_number_detected}")
        print(f"MRP: {r.mrp_detected}")
        print(f"Raw text: {r.raw_text[:100] if r.raw_text else None}...")
        print(f"Failure reason: {r.failure_reason}")
finally:
    db.close()
