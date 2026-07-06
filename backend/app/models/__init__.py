"""
models/__init__.py

Import every model here so SQLAlchemy's Base.metadata knows about all
tables before create_all() or Alembic introspects the schema.

Usage in main.py:
    from app.models import product, inventory, validation_record
"""

from app.models.product import Product
from app.models.inventory import InventoryItem
from app.models.validation_record import ValidationRecord
from app.models.user import User                          # required for users table creation
from app.models.financial_profile import ProductFinancialProfile
from app.models.warehouse import (
    Warehouse,
    TransportCostConfiguration,
    WarehouseConfiguration,
    WarehouseDemandProfile,
    WarehouseTransferMatrix,
    SupplierReturnPolicy,
    OptimizationConfiguration,
)

__all__ = [
    "Product",
    "InventoryItem",
    "ValidationRecord",
    "User",
    "ProductFinancialProfile",
    "Warehouse",
    "TransportCostConfiguration",
    "WarehouseConfiguration",
    "WarehouseDemandProfile",
    "WarehouseTransferMatrix",
    "SupplierReturnPolicy",
    "OptimizationConfiguration",
]



