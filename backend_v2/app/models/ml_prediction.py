"""
models/ml_prediction.py — ML team's shelf-life prediction for a batch.

The backend team writes a record here ONLY when the ML team
returns a result via webhook or API call.
Backend never populates predicted_decision itself.

Final decisions live here — NOT on inventory_items.
  ACCEPTED | PRIORITY_SALE | REJECTED | REQUIRES_REVIEW
"""

import uuid

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id                      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    inventory_item_id       = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)

    # ── ML model metadata ─────────────────────────────────────
    model_name              = Column(String(200), nullable=True)   # e.g. "expiry-v2.1"
    model_version           = Column(String(50),  nullable=True)

    # ── Parsed dates (ML team's interpretation of OCR output) ─
    predicted_mfg_date      = Column(Date,  nullable=True)
    predicted_expiry_date   = Column(Date,  nullable=True)
    predicted_remaining_days = Column(Integer, nullable=True)

    # ── Final decision from ML ────────────────────────────────
    # ACCEPTED | PRIORITY_SALE | REJECTED | REQUIRES_REVIEW
    predicted_decision      = Column(String(30), nullable=True, index=True)
    decision_confidence     = Column(Float,  nullable=True)  # 0.0–1.0
    decision_reason         = Column(Text,   nullable=True)

    # ── Raw ML output (full JSON from model) ─────────────────
    raw_prediction_payload  = Column(Text,   nullable=True)  # full JSON string

    # ── Processing status ─────────────────────────────────────
    # pending | completed | failed
    prediction_status       = Column(String(20), nullable=False, default="pending")
    failure_reason          = Column(Text,   nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    predicted_at            = Column(DateTime(timezone=True), nullable=True)
    created_at              = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at              = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    inventory_item          = relationship("InventoryItem", back_populates="ml_predictions")
