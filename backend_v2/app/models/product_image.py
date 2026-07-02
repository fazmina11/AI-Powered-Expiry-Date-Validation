"""
models/product_image.py — Uploaded product or label images.

Each image record stores the file path/URL, the image type,
and its processing status. OCR and ML teams consume these records
to extract label text and make predictions.
"""

import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id      = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    scan_session_id = Column(UUID(as_uuid=True), ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)

    # ── File info ─────────────────────────────────────────────
    file_path       = Column(String(500), nullable=False)   # server-side storage path
    file_url        = Column(String(500), nullable=True)    # public URL if served via CDN
    file_size_bytes = Column(Integer,     nullable=True)
    mime_type       = Column(String(100), nullable=True)    # image/jpeg, image/png, etc.

    # ── Image classification ──────────────────────────────────
    image_type      = Column(String(50),  nullable=True)
                   # front_label | back_label | side_label | product_photo | barcode_close_up

    # ── Processing state ──────────────────────────────────────
    # uploaded       = file received, not yet processed
    # ocr_pending    = queued for OCR
    # ocr_completed  = OCR finished, see ocr_results table
    # failed         = processing failed
    processing_status = Column(String(30), nullable=False, default="uploaded")

    notes           = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    uploaded_at     = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    product         = relationship("Product", back_populates="product_images")
    scan_session    = relationship("ScanSession", back_populates="product_images")
    ocr_results     = relationship("OCRResult", back_populates="product_image", cascade="all, delete-orphan")
