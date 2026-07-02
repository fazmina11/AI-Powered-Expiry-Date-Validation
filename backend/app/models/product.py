"""
models/product.py — Product ORM model.

A Product represents a SKU/barcode registered in the system.
One product can have many InventoryItem batches.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String,  nullable=False)
    sku         = Column(String,  unique=True, index=True, nullable=False)
    barcode     = Column(String,  unique=True, index=True, nullable=False)
    category    = Column(String,  nullable=True)
    image_url   = Column(String,  nullable=True)   # ML/OCR placeholder for future phases
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="product")
