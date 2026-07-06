"""
models/financial_profile.py — ProductFinancialProfile ORM model.

Stores financial metadata for a product such as purchase price, MRP,
margin percentage, currency, and supplier return policies.
"""

import uuid
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Uuid, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductFinancialProfile(Base):
    __tablename__ = "product_financial_profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    # References products.id which is Integer type
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)
    default_profit_margin_percent = Column(Numeric(5, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    supplier_return_allowed = Column(Boolean, default=True, nullable=False)
    supplier_return_percent = Column(Numeric(5, 2), default=100.00, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="financial_profile")
