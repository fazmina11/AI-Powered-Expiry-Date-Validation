import uuid

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    product_image_id = Column(UUID(as_uuid=True), ForeignKey("product_images.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    scan_session_id = Column(UUID(as_uuid=True), ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True)

    raw_text = Column(Text, nullable=True)
    ocr_engine = Column(String(100), nullable=True)
    ocr_engine_version = Column(String(50), nullable=True)
    extracted_text_blocks = Column(JSON, nullable=True)
    overall_confidence = Column(Float, nullable=True)

    ocr_confidence = Column(Numeric(5, 4), nullable=True)
    extracted_product_name = Column(String(255), nullable=True)
    extracted_brand = Column(String(150), nullable=True)
    extracted_description = Column(Text, nullable=True)
    extracted_ingredients_text = Column(Text, nullable=True)
    extracted_nutrition_text = Column(Text, nullable=True)
    candidate_mfg_date = Column(Date, nullable=True)
    candidate_expiry_date = Column(Date, nullable=True)
    candidate_packed_date = Column(Date, nullable=True)
    best_before_text = Column(String(255), nullable=True)
    batch_number_detected = Column(String(100), nullable=True)
    mrp_detected = Column(Numeric(10, 2), nullable=True)
    date_parse_confidence = Column(Numeric(5, 4), nullable=True)
    response_json = Column(JSONB, nullable=True)

    ocr_status = Column(String(30), nullable=False, default="pending")
    failure_reason = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    product_image = relationship("ProductImage", back_populates="ocr_results")
    product = relationship("Product")
    scan_session = relationship("ScanSession", back_populates="ocr_results")
    inventory_item = relationship("InventoryItem", back_populates="ocr_results", foreign_keys=[inventory_item_id])
    manual_reviews = relationship("ManualReview", back_populates="ocr_result")
