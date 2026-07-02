"""
models/barcode_scan.py — Records every barcode scanning event.

A scan event captures the raw barcode value, the type/format detected,
and the device or session that produced it. Multiple scans can reference
the same product (or none, if the barcode is unrecognised).
"""

import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class BarcodeScan(Base):
    __tablename__ = "barcode_scans"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # ── Resolved product (nullable — barcode may not match any product) ──
    product_id      = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    scan_session_id = Column(UUID(as_uuid=True), ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)

    # ── Raw scan data ─────────────────────────────────────────
    raw_barcode     = Column(String(255), nullable=False)   # value as scanned
    barcode_type    = Column(String(20),  nullable=True)    # EAN13 / QR / etc.
    scan_source     = Column(String(100), nullable=True)    # device_id, session_id, api_client

    # ── Status ────────────────────────────────────────────────
    # resolved    = barcode matched a product
    # unresolved  = no product found for this barcode
    scan_status     = Column(String(20), nullable=False, default="unresolved")

    notes           = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    scanned_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    product         = relationship("Product", back_populates="barcode_scans")
    scan_session    = relationship("ScanSession", back_populates="barcode_scans")
    inventory_items = relationship("InventoryItem", back_populates="barcode_scan")
