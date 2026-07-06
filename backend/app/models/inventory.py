"""
models/inventory.py — InventoryItem ORM model.

An InventoryItem represents a single batch of a product received
during a warehouse intake scan. The shelf-life decision and financial
snapshots are stored on this record.
"""

from decimal import Decimal
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Numeric, JSON, Boolean
from sqlalchemy.orm import relationship, validates
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
    
    # Financial fields (Phase 2)
    quantity            = Column(Integer, default=1, nullable=False)
    purchase_price      = Column(Numeric(10, 2), nullable=True)
    mrp                 = Column(Numeric(10, 2), nullable=True)
    inventory_cost      = Column(Numeric(12, 2), nullable=True)
    currency            = Column(String(10), default="INR", nullable=False)
    supplier_return_allowed = Column(Boolean, default=True, nullable=True)
    supplier_return_percent = Column(Numeric(5, 2), default=100.00, nullable=True)
    financial_profile_snapshot = Column(JSON, nullable=True)

    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    product             = relationship("Product", back_populates="inventory_items")
    validation_records  = relationship("ValidationRecord", back_populates="inventory_item")

    def calculate_inventory_cost(self) -> Decimal:
        """Helper function to calculate quantity * purchase_price using Decimal."""
        if self.quantity is not None and self.purchase_price is not None:
            return Decimal(str(self.quantity)) * Decimal(str(self.purchase_price))
        return Decimal("0.00")

    @validates("quantity", "purchase_price")
    def sync_inventory_cost(self, key, value):
        """Synchronize inventory_cost whenever quantity or purchase_price is set."""
        qty = value if key == "quantity" else self.quantity
        price = value if key == "purchase_price" else self.purchase_price

        if qty is not None and price is not None:
            # Trigger synchronization using Decimal
            self.inventory_cost = Decimal(str(qty)) * Decimal(str(price))
        else:
            self.inventory_cost = None
        return value
