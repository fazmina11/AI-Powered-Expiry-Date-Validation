"""
models/product.py — Master product catalogue.

One Product can have many:
  - BarcodeScan records (each physical scan event)
  - ProductImage records (uploaded label / product photos)
  - InventoryItem records (each warehouse intake batch)
"""

import uuid

from sqlalchemy import Boolean, Column, Numeric, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    # ── Identity ─────────────────────────────────────────────
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name            = Column(String(255),  nullable=False)
    brand           = Column(String(255),  nullable=True)
    manufacturer    = Column(String(255),  nullable=True)
    sku             = Column(String(100),  unique=True, index=True, nullable=False)
    barcode         = Column(String(100),  unique=True, index=True, nullable=False)
    barcode_type    = Column(String(20),   nullable=False, default="EAN13")
                   # EAN13 | EAN8 | UPC-A | QR | CODE128 | DATAMATRIX

    # ── Classification ────────────────────────────────────────
    category        = Column(String(100),  nullable=True)
    sub_category    = Column(String(100),  nullable=True)
    description     = Column(Text,         nullable=True)
    net_quantity    = Column(String(100),  nullable=True)
    unit            = Column(String(50),   nullable=True)
    mrp             = Column(Numeric(10, 2), nullable=True)
    currency        = Column(String(10),   nullable=False, default="INR")
    country_of_origin = Column(String(100), nullable=True)
    product_type    = Column(String(100),  nullable=True)

    # ── Storage ───────────────────────────────────────────────
    default_storage_type = Column(String(50), nullable=True)
                   # ambient | refrigerated | frozen | controlled
    shelf_life_label = Column(String(255), nullable=True)

    # ── Media ─────────────────────────────────────────────────
    image_url       = Column(String(500),  nullable=True)
                   # URL to primary product image (populated by image upload)
    product_image_url = Column(String(500), nullable=True)

    # ── Status ────────────────────────────────────────────────
    is_active       = Column(Boolean, default=True, nullable=False)
    is_perishable   = Column(Boolean, default=False, nullable=False)

    # ── Timestamps ────────────────────────────────────────────
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    barcode_scans   = relationship("BarcodeScan",  back_populates="product", cascade="all, delete-orphan")
    product_images  = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="product")
    identifiers     = relationship("ProductIdentifier", back_populates="product", cascade="all, delete-orphan")
    ingredients     = relationship("ProductIngredient", back_populates="product", cascade="all, delete-orphan")
    allergens       = relationship("ProductAllergen", back_populates="product", cascade="all, delete-orphan")
    nutrition       = relationship("ProductNutrition", back_populates="product", cascade="all, delete-orphan", uselist=False)
    storage_requirements = relationship("ProductStorageRequirement", back_populates="product", cascade="all, delete-orphan")
    enrichment_logs = relationship("ExternalProductEnrichmentLog", back_populates="product")

    def __repr__(self):
        return f"<Product sku={self.sku} name={self.name!r}>"
