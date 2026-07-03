import uuid
import json
import logging
from sqlalchemy.orm import Session
from typing import Any

from app.models.product import Product
from app.models.barcode_scan import BarcodeScan
from app.models.product_image import ProductImage
from app.models.ocr_result import OCRResult
from app.schemas.product_intelligence_schema import ProductIntelligence

log = logging.getLogger("transaction_service")

class TransactionService:
    @staticmethod
    def persist_scan_pipeline_results(
        db: Session,
        result: ProductIntelligence,
        saved_file_path: str
    ) -> Any:
        try:
            barcode_val = result.barcode.value
            product = None
            
            if barcode_val:
                product = db.query(Product).filter(Product.barcode == barcode_val).first()
                
            if not product:
                product = Product(
                    name=result.product.name or "Unknown Scanned Product",
                    barcode=barcode_val or f"UNKNOWN-{uuid.uuid4()}",
                    brand=result.product.brand
                )
                db.add(product)
                db.commit()
                db.refresh(product)
                
            b_scan = BarcodeScan(
                raw_barcode=barcode_val or "NO_BARCODE",
                product_id=product.id,
                scan_status="resolved" if barcode_val else "unresolved"
            )
            db.add(b_scan)
            db.commit()
            db.refresh(b_scan)
            
            p_image = ProductImage(
                file_path=saved_file_path,
                product_id=product.id,
                processing_status="ocr_completed"
            )
            db.add(p_image)
            db.commit()
            db.refresh(p_image)
            
            ocr_res = OCRResult(
                product_image_id=p_image.id,
                product_id=product.id,
                raw_text=result.ocr.raw_text,
                overall_confidence=result.ocr.confidence,
                candidate_mfg_date=result.manufacturing.manufacturing_date,
                candidate_expiry_date=result.expiry.expiry_date,
                batch_number_detected=result.batch.batch_number,
                ocr_status="completed"
            )
            db.add(ocr_res)
            db.commit()
            db.refresh(ocr_res)
            
            
            return {
                "barcode_scan_id": str(b_scan.id),
                "product_image_id": str(p_image.id),
                "ocr_result_id": str(ocr_res.id),
                "product_id": str(product.id)
            }
        except Exception as e:
            db.rollback()
            log.error(f"Transaction failed: {e}")
            raise
