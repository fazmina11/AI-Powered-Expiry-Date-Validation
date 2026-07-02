"""
services/scan_session_service.py — Orchestrates scanning intake session workflows.
"""

from typing import Optional, Any
from sqlalchemy.orm import Session

from app.models.inventory_item import InventoryItem
from app.models.product_image import ProductImage
from app.models.barcode_scan import BarcodeScan
from app.services.barcode_service import process_barcode_scan
from app.services.ocr_service import trigger_ocr_processing
from app.services.alert_service import log_audit_event


def start_intake_session(
    db: Session,
    raw_barcode: str,
    barcode_type: Optional[str] = None,
    scan_source: Optional[str] = None,
) -> BarcodeScan:
    """
    Step 1: Scans a barcode, registers scan event, and resolves the product.
    """
    scan_event = process_barcode_scan(
        db=db,
        raw_barcode=raw_barcode,
        barcode_type=barcode_type,
        scan_source=scan_source
    )
    
    log_audit_event(
        db=db,
        event_type="scan.session_started",
        entity_type="barcode_scan",
        entity_id=str(scan_event.id),
        change_summary=f"Intake session started for barcode {raw_barcode}."
    )
    
    return scan_event


def create_session_inventory_item(
    db: Session,
    barcode_scan_id: Any,
    batch_number: str,
    quantity: int = 1,
    unit: str = "units",
    intake_notes: Optional[str] = None,
) -> InventoryItem:
    """
    Step 2: Creates the inventory item from the scan context and batch details.
    """
    scan = db.query(BarcodeScan).filter(BarcodeScan.id == barcode_scan_id).first()
    if not scan:
        raise ValueError(f"Barcode scan ID {barcode_scan_id} not found.")

    if not scan.product_id:
        raise ValueError("Cannot intake inventory for an unresolved barcode scan.")

    # Create the InventoryItem
    inventory_item = InventoryItem(
        product_id=scan.product_id,
        barcode_scan_id=scan.id,
        batch_number=batch_number,
        pipeline_status="PENDING_OCR",
        quantity=quantity,
        unit=unit,
        intake_notes=intake_notes,
    )
    
    db.add(inventory_item)
    db.commit()
    db.refresh(inventory_item)

    log_audit_event(
        db=db,
        event_type="inventory.created",
        entity_type="inventory_item",
        entity_id=str(inventory_item.id),
        change_summary=f"Created inventory item for SKU {scan.product.sku} BATCH {batch_number}"
    )

    return inventory_item


def attach_label_image_and_trigger_ocr(
    db: Session,
    inventory_item_id: Any,
    file_path: str,
    file_url: Optional[str] = None,
    file_size_bytes: Optional[int] = None,
    mime_type: Optional[str] = None,
    image_type: str = "back_label",
) -> ProductImage:
    """
    Step 3: Attaches a label photo to the intake item and initiates the OCR process.
    """
    item = db.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
    if not item:
        raise ValueError(f"Inventory item ID {inventory_item_id} not found.")

    # Create ProductImage
    image = ProductImage(
        product_id=item.product_id,
        file_path=file_path,
        file_url=file_url,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
        image_type=image_type,
        processing_status="uploaded"
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    log_audit_event(
        db=db,
        event_type="image.attached",
        entity_type="product_image",
        entity_id=str(image.id),
        change_summary=f"Attached {image_type} image to product {item.product.sku}"
    )

    # Automatically trigger OCR pipeline
    trigger_ocr_processing(db=db, product_image_id=image.id, inventory_item_id=item.id)

    return image
