"""
models/__init__.py
Import all models here so Base.metadata registers every table
before create_all() or Alembic env.py inspects the schema.
"""

from app.models.product import Product
from app.models.catalog import (
    ProductIdentifier,
    ProductIngredient,
    ProductAllergen,
    ProductNutrition,
    ProductStorageRequirement,
)
from app.models.operations import (
    Supplier,
    Warehouse,
    StorageLocation,
    ScanSession,
    InventoryMovement,
    ScanAlert,
    ExternalProductEnrichmentLog,
)
from app.models.barcode_scan import BarcodeScan
from app.models.product_image import ProductImage
from app.models.ocr_result import OCRResult
from app.models.inventory_item import InventoryItem
from app.models.storage_context import StorageContext
from app.models.ml_prediction import MLPrediction
from app.models.manual_review import ManualReview
from app.models.audit_log import AuditLog
from app.models.user import User

__all__ = [
<<<<<<< HEAD
    "Product", "BarcodeScan", "ProductImage", "OCRResult",
    "InventoryItem", "StorageContext", "MLPrediction",
    "ManualReview", "AuditLog",
    "User",
=======
    "Product", "ProductIdentifier", "ProductIngredient",
    "ProductAllergen", "ProductNutrition", "ProductStorageRequirement",
    "Supplier", "Warehouse", "StorageLocation", "ScanSession",
    "BarcodeScan", "ProductImage", "OCRResult", "InventoryItem",
    "InventoryMovement", "ManualReview", "ScanAlert", "AuditLog",
    "ExternalProductEnrichmentLog", "StorageContext", "MLPrediction",
>>>>>>> 0f02161 (Update project for Harish branch)
]
