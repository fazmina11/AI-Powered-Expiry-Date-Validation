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

# PGN Phase 1 — Community Product Reporting System
from app.community.models.community_user import CommunityUser as PGNCommunityUser  # noqa: F401
from app.community.models.product_report  import ProductReport  as PGNProductReport  # noqa: F401
from app.community.models.report_image    import ReportImage    as PGNReportImage    # noqa: F401
from app.community.models.report_credibility import ReportCredibility as PGNReportCredibility  # noqa: F401
from app.community.models.issue_cluster   import (
    IssueCluster as PGNIssueCluster,
    ClusterReport as PGNClusterReport,
    ClusterLocation as PGNClusterLocation,
)  # noqa: F401
from app.community.models.cluster_intelligence import ClusterIntelligence as PGNClusterIntelligence  # noqa: F401
from app.community.models.safety_alert import (
    SafetyAlert as PGNSafetyAlert,
    AlertHistory as PGNAlertHistory,
    AlertNotification as PGNAlertNotification,
)  # noqa: F401
from app.community.models.investigation import (
    InvestigationCase as PGNInvestigationCase,
    InvestigationNote as PGNInvestigationNote,
    CaseEvidence as PGNCaseEvidence,
    CaseTimeline as PGNCaseTimeline,
)  # noqa: F401

__all__ = [
    "Product", "ProductIdentifier", "ProductIngredient",
    "ProductAllergen", "ProductNutrition", "ProductStorageRequirement",
    "Supplier", "Warehouse", "StorageLocation", "ScanSession",
    "BarcodeScan", "ProductImage", "OCRResult", "InventoryItem",
    "InventoryMovement", "ManualReview", "ScanAlert", "AuditLog",
    "ExternalProductEnrichmentLog", "ExternalProductCache",
    "ProductLookupLog", "UnknownProductRequest", "ProductQuestionLog",
    "StorageContext", "MLPrediction", "User",
    "PGNCommunityUser", "PGNProductReport", "PGNReportImage", "PGNReportCredibility",
    "PGNIssueCluster", "PGNClusterReport", "PGNClusterLocation", "PGNClusterIntelligence",
    "PGNSafetyAlert", "PGNAlertHistory", "PGNAlertNotification",
    "PGNInvestigationCase", "PGNInvestigationNote", "PGNCaseEvidence", "PGNCaseTimeline",
]

