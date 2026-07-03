import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_status = Column(String(50), nullable=False, default="IN_PROGRESS", index=True)
    operator_name = Column(String(150), nullable=True)
    device_id = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    barcode_scans = relationship("BarcodeScan", back_populates="scan_session")
    product_images = relationship("ProductImage", back_populates="scan_session")
    ocr_results = relationship("OCRResult", back_populates="scan_session")
    inventory_items = relationship("InventoryItem", back_populates="scan_session")
    manual_reviews = relationship("ManualReview", back_populates="scan_session")
    scan_alerts = relationship("ScanAlert", back_populates="scan_session")
