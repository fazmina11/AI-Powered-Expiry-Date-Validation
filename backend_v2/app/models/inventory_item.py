"""
models/inventory_item.py — A single batch received during warehouse intake.

Status lifecycle (backend-only — no shelf-life decisions here):
  PENDING_OCR       → batch scanned in, waiting for image processing
  OCR_COMPLETED     → OCR text extracted, waiting for ML
  PENDING_ML_REVIEW → sent to ML team's queue
  ML_COMPLETED      → ML team returned a prediction
  MANUAL_REVIEW     → flagged for human inspection

Final decisions (ACCEPTED, REJECTED, PRIORITY_SALE) come from
the ML team and are stored in the ml_predictions table, NOT here.
"""

import uuid

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # ── Source references ─────────────────────────────────────
    product_id          = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    barcode_scan_id     = Column(UUID(as_uuid=True), ForeignKey("barcode_scans.id", ondelete="SET NULL"), nullable=True)
    scan_session_id     = Column(UUID(as_uuid=True), ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    ocr_result_id       = Column(
        UUID(as_uuid=True),
        ForeignKey("ocr_results.id", ondelete="SET NULL", use_alter=True, name="fk_inventory_items_ocr_result_id"),
        nullable=True,
        index=True,
    )
    supplier_id         = Column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True)
    warehouse_id        = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True, index=True)
    storage_location_id = Column(UUID(as_uuid=True), ForeignKey("storage_locations.id", ondelete="SET NULL"), nullable=True, index=True)

    # ── Batch identity ────────────────────────────────────────
    batch_number        = Column(String(100), nullable=True, index=True)

    # ── Dates (entered by warehouse staff or extracted by OCR) ───────────
    # These are raw inputs. The ML team validates and uses them.
    manufacturing_date  = Column(Date, nullable=True)
    expiry_date         = Column(Date, nullable=True)
    packed_date         = Column(Date, nullable=True)

    # ── Backend pipeline status ───────────────────────────────
    # PENDING_OCR | OCR_COMPLETED | PENDING_ML_REVIEW | ML_COMPLETED | MANUAL_REVIEW
    pipeline_status     = Column(String(30), nullable=False, default="PENDING_OCR", index=True)
    status_reason       = Column(Text, nullable=True)  # reason for current status
    intake_source       = Column(String(50), nullable=False, default="OCR_SCAN")
    intake_status       = Column(String(50), nullable=False, default="DATA_INCOMPLETE", index=True)
    operator_decision   = Column(String(100), nullable=True)

    # ── Quantity ──────────────────────────────────────────────
    quantity            = Column(Integer, nullable=True, default=1)
    unit                = Column(String(20), nullable=True)  # units | cartons | pallets

    # ── Notes ─────────────────────────────────────────────────
    intake_notes        = Column(Text, nullable=True)
    notes               = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    intake_at           = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    product             = relationship("Product",       back_populates="inventory_items")
    barcode_scan        = relationship("BarcodeScan",   back_populates="inventory_items")
    scan_session        = relationship("ScanSession", back_populates="inventory_items")
    selected_ocr_result = relationship("OCRResult", foreign_keys=[ocr_result_id])
    supplier            = relationship("Supplier", back_populates="inventory_items")
    warehouse           = relationship("Warehouse", back_populates="inventory_items")
    storage_location    = relationship("StorageLocation", back_populates="inventory_items")
    storage_context     = relationship("StorageContext", back_populates="inventory_item", uselist=False)
    ocr_results         = relationship("OCRResult",     back_populates="inventory_item", foreign_keys="OCRResult.inventory_item_id")
    ml_predictions      = relationship("MLPrediction",  back_populates="inventory_item")
    manual_reviews      = relationship("ManualReview",  back_populates="inventory_item")
    movements           = relationship("InventoryMovement", back_populates="inventory_item")
    scan_alerts         = relationship("ScanAlert", back_populates="inventory_item")
