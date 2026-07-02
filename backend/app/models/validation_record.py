"""
models/validation_record.py — ValidationRecord ORM model.

A ValidationRecord logs the result of a date extraction attempt
for an InventoryItem. In Phase 1 these are created manually.
Fields marked as ML/OCR placeholders will be populated by the
vision pipeline in a future phase.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ValidationRecord(Base):
    __tablename__ = "validation_records"

    id                    = Column(Integer, primary_key=True, index=True)
    inventory_item_id     = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)

    # ML/OCR placeholder fields — populated by the vision pipeline (future phase)
    raw_text              = Column(Text,    nullable=True)
    extracted_mfg_date    = Column(Date,    nullable=True)
    extracted_expiry_date = Column(Date,    nullable=True)
    confidence_score      = Column(Float,   nullable=True)

    validation_status     = Column(String,  default="PENDING", nullable=False)
    failure_reason        = Column(Text,    nullable=True)
    created_at            = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    inventory_item        = relationship("InventoryItem", back_populates="validation_records")
