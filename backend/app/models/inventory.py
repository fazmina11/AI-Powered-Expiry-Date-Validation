"""
models/inventory.py — InventoryItem ORM model.

An InventoryItem represents a single batch of a product received
during a warehouse intake scan. The shelf-life decision is stored
on this record after validation.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id                  = Column(Integer, primary_key=True, index=True)
    product_id          = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_number        = Column(String,  index=True, nullable=True)
    manufacturing_date  = Column(Date,    nullable=True)
    expiry_date         = Column(Date,    nullable=True)
    remaining_days      = Column(Integer, nullable=True)  # computed at intake, stored
    status              = Column(String,  default="PENDING", nullable=False, index=True)
    decision_reason     = Column(Text,    nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    product             = relationship("Product", back_populates="inventory_items")
    validation_records  = relationship("ValidationRecord", back_populates="inventory_item")
