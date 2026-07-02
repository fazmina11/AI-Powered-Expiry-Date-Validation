import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scan_session_id = Column(UUID(as_uuid=True), ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=True, index=True)
    ocr_result_id = Column(UUID(as_uuid=True), ForeignKey("ocr_results.id", ondelete="SET NULL"), nullable=True, index=True)

    review_type = Column(String(50), nullable=False, default="OCR_CORRECTION")
    original_mfg_date = Column(Date, nullable=True)
    original_expiry_date = Column(Date, nullable=True)
    corrected_mfg_date = Column(Date, nullable=True)
    corrected_expiry_date = Column(Date, nullable=True)
    corrected_batch_number = Column(String(100), nullable=True)
    corrected_description = Column(Text, nullable=True)

    reviewer_id = Column(String(200), nullable=True)
    reviewer_name = Column(String(150), nullable=True)
    reviewer_role = Column(String(100), nullable=True)
    reviewer_note = Column(Text, nullable=True)

    human_decision = Column(String(30), nullable=True, index=True)
    review_notes = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    review_status = Column(String(20), nullable=False, default="pending", index=True)

    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scan_session = relationship("ScanSession", back_populates="manual_reviews")
    inventory_item = relationship("InventoryItem", back_populates="manual_reviews")
    ocr_result = relationship("OCRResult", back_populates="manual_reviews")
