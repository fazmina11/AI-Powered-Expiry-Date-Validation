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
    InventoryMovement,
    ExternalProductEnrichmentLog,
)
from app.models.scan_session import ScanSession
from app.models.scan_alert import ScanAlert
from app.models.barcode_scan import BarcodeScan
from app.models.product_image import ProductImage
from app.models.ocr_result import OCRResult
from app.models.inventory import InventoryItem
from app.models.storage_context import StorageContext
from app.models.ml_prediction import MLPrediction
from app.models.manual_review import ManualReview
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.product_lookup import ExternalProductCache, ProductLookupLog, UnknownProductRequest
from app.models.product_question import ProductQuestionLog
from app.community.models import (
    CommunityUser,
    ProductReport,
    ReportImage,
    ReportCredibility,
    IssueCluster,
    ClusterReport,
    ClusterLocation,
    ClusterIntelligence,
    SafetyAlert,
    AlertHistory,
    AlertNotification,
    InvestigationCase,
    InvestigationNote,
    CaseEvidence,
    CaseTimeline,
)

__all__ = [
    "Product", "ProductIdentifier", "ProductIngredient",
    "ProductAllergen", "ProductNutrition", "ProductStorageRequirement",
    "Supplier", "Warehouse", "StorageLocation", "ScanSession",
    "BarcodeScan", "ProductImage", "OCRResult", "InventoryItem",
    "InventoryMovement", "ManualReview", "ScanAlert", "AuditLog",
    "ExternalProductEnrichmentLog", "ExternalProductCache",
    "ProductLookupLog", "UnknownProductRequest", "ProductQuestionLog",
    "StorageContext", "MLPrediction", "User", "CommunityUser",
    "ProductReport", "ReportImage", "ReportCredibility", "IssueCluster",
    "ClusterReport", "ClusterLocation", "ClusterIntelligence",
    "SafetyAlert", "AlertHistory", "AlertNotification",
    "InvestigationCase", "InvestigationNote", "CaseEvidence", "CaseTimeline"
]

