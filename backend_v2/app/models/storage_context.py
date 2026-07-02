"""
models/storage_context.py — Where and how a batch is physically stored.

One InventoryItem has one StorageContext (one-to-one).
This gives the ML team environmental context (temperature zone,
location) when making shelf-life predictions.
"""

import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class StorageContext(Base):
    __tablename__ = "storage_contexts"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    inventory_item_id   = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, unique=True)

    # ── Physical location ─────────────────────────────────────
    warehouse_id        = Column(String(100), nullable=True)
    zone                = Column(String(100), nullable=True)   # e.g. "Zone-A", "Cold-Room-1"
    aisle               = Column(String(50),  nullable=True)
    shelf               = Column(String(50),  nullable=True)
    bin_location        = Column(String(100), nullable=True)

    # ── Storage type ──────────────────────────────────────────
    # ambient | refrigerated | frozen | controlled
    storage_type        = Column(String(50), nullable=True)

    # ── Environmental readings (optional IoT data) ────────────
    temperature_celsius = Column(Float, nullable=True)
    humidity_percent    = Column(Float, nullable=True)

    notes               = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    recorded_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    inventory_item      = relationship("InventoryItem", back_populates="storage_context")
