"""
services/ocr_service.py — Interfaces with the OCR pipeline to retrieve raw labels text.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.ocr_result import OCRResult
from app.models.product_image import ProductImage
from app.models.inventory_item import InventoryItem


def trigger_ocr_processing(
    db: Session,
    product_image_id: Any,
    inventory_item_id: Optional[Any] = None,
    ocr_engine: str = "mock-vision-v2",
) -> OCRResult:
    """
    Kicks off OCR extraction workflow for a specific product image.
    Updates ProductImage.processing_status to ocr_pending.
    Creates and returns a pending OCRResult record.
    """
    image = db.query(ProductImage).filter(ProductImage.id == product_image_id).first()
    if not image:
        raise ValueError(f"ProductImage with ID {product_image_id} not found")

    image.processing_status = "ocr_pending"
    db.commit()

    # Create a pending OCR record
    ocr_record = OCRResult(
        product_image_id=product_image_id,
        inventory_item_id=inventory_item_id,
        ocr_engine=ocr_engine,
        ocr_status="pending",
    )
    db.add(ocr_record)
    db.commit()
    db.refresh(ocr_record)
    return ocr_record


def complete_ocr_processing(
    db: Session,
    ocr_record_id: Any,
    raw_text: str,
    extracted_text_blocks: Optional[List[Dict[str, Any]]] = None,
    overall_confidence: float = 1.0,
    ocr_engine_version: Optional[str] = None,
) -> OCRResult:
    """
    Called when OCR extraction finishes successfully.
    Saves extracted data, updates statuses on both OCRResult and ProductImage.
    """
    ocr_record = db.query(OCRResult).filter(OCRResult.id == ocr_record_id).first()
    if not ocr_record:
        raise ValueError(f"OCRResult record with ID {ocr_record_id} not found")

    ocr_record.raw_text = raw_text
    ocr_record.extracted_text_blocks = extracted_text_blocks or []
    ocr_record.overall_confidence = overall_confidence
    ocr_record.ocr_engine_version = ocr_engine_version
    ocr_record.ocr_status = "completed"
    ocr_record.processed_at = datetime.utcnow()

    # Update associated image state
    if ocr_record.product_image:
        ocr_record.product_image.processing_status = "ocr_completed"

    # Update associated inventory item state if applicable
    if ocr_record.inventory_item:
        ocr_record.inventory_item.pipeline_status = "OCR_COMPLETED"

    db.commit()
    db.refresh(ocr_record)
    return ocr_record


def fail_ocr_processing(
    db: Session,
    ocr_record_id: Any,
    failure_reason: str,
) -> OCRResult:
    """Handles marking OCR extraction as failed."""
    ocr_record = db.query(OCRResult).filter(OCRResult.id == ocr_record_id).first()
    if not ocr_record:
        raise ValueError(f"OCRResult record with ID {ocr_record_id} not found")

    ocr_record.ocr_status = "failed"
    ocr_record.failure_reason = failure_reason
    ocr_record.processed_at = datetime.utcnow()

    if ocr_record.product_image:
        ocr_record.product_image.processing_status = "failed"

    if ocr_record.inventory_item:
        ocr_record.inventory_item.pipeline_status = "MANUAL_REVIEW"
        ocr_record.inventory_item.status_reason = f"OCR Failed: {failure_reason}"

    db.commit()
    db.refresh(ocr_record)
    return ocr_record
