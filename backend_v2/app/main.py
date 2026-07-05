"""
main.py — Phase 2 FastAPI application entry point.

Routes will be added in upcoming phases.
This file establishes the app, health check, and DB connectivity probe.
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    integrity_exception_handler,
    database_exception_handler,
    generic_exception_handler,
)
from app.middleware.response_standardizer import ResponseStandardizationMiddleware

from app.config import settings
from app.database import check_db_connection, get_db

# Register all models on Base.metadata
from app.models import (  # noqa: F401
    Product, ProductIdentifier, ProductIngredient, ProductAllergen,
    ProductNutrition, ProductStorageRequirement, Supplier, Warehouse,
    StorageLocation, ScanSession, BarcodeScan, ProductImage, OCRResult,
    InventoryItem, InventoryMovement, ManualReview, ScanAlert, AuditLog,
    ExternalProductEnrichmentLog, ExternalProductCache, ProductLookupLog,
    UnknownProductRequest, ProductQuestionLog, StorageContext, MLPrediction,
)
from app.routes.auth import router as auth_router
from app.routes.ocr import router as ocr_router
from app.routes.barcode import router as barcode_router
from app.routes.inventory import router as inventory_router
from app.routes.scan_session import router as scan_session_router
from app.routes.scan import router as scan_router
from app.routes import product_lookup_routes, product_question_routes
from app.community.routes.user_routes   import router as community_users_router
from app.community.routes.report_routes import router as community_reports_router
from app.community.routes.credibility_routes import router as community_credibility_router
from app.community.routes.cluster_routes     import router as community_clusters_router
from app.community.routes.intelligence_routes import router as community_intelligence_router
from app.community.routes.alert_routes        import router as community_alerts_router
from app.community.routes.case_routes         import router as community_cases_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ok = check_db_connection()
    status = "connected" if db_ok else "UNAVAILABLE"
    print(f"[startup] database: {status} | env: {settings.APP_ENV} | v{settings.APP_VERSION}")
    yield


app = FastAPI(
    title="AI-Powered Expiry Validation Platform",
    description=(
        "Enterprise backend for OCR-based product scanning, inventory "
        "management, community reporting, safety intelligence, alerts, "
        "and investigation management."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8050",
        "http://127.0.0.1:8050",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(ResponseStandardizationMiddleware)

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
app.include_router(auth_router)
app.include_router(ocr_router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(barcode_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(scan_session_router, prefix="/api/v1/session", tags=["Session"])
app.include_router(scan_router, prefix="/api/scan", tags=["Scan"])
app.include_router(product_lookup_routes.router, prefix="/api/v1", tags=["Product Lookup"])
app.include_router(product_question_routes.router, prefix="/api/v1", tags=["Product Questions"])

# PGN Phase 1 — Community Product Reporting System
app.include_router(community_users_router,   prefix="/api/v1/community", tags=["Community Users"])
app.include_router(community_reports_router, prefix="/api/v1/community", tags=["Community Reports"])
app.include_router(community_credibility_router, prefix="/api/v1/community", tags=["Report Credibility"])
app.include_router(community_clusters_router, prefix="/api/v1/community", tags=["Issue Clusters"])
app.include_router(community_intelligence_router, prefix="/api/v1/community", tags=["Community Intelligence"])
app.include_router(community_alerts_router, prefix="/api/v1/community", tags=["Safety Alerts"])
app.include_router(community_cases_router, prefix="/api/v1/community", tags=["Investigation Cases"])


@app.get("/debug-db", tags=["debug"])
def debug_db(db = Depends(get_db)):
    try:
        from app.models.ocr_result import OCRResult
        results = db.query(OCRResult).all()
        return {"success": True, "count": len(results)}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@app.get("/health", tags=["health"])
def health_check():
    db_ok = check_db_connection()
    return {
        "status":   "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "version":  settings.APP_VERSION,
        "env":      settings.APP_ENV,
    }
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint for the AI-Powered Expiry Validation Backend.
    Provides quick navigation to documentation and health endpoints.
    """
    return {
        "success": True,
        "message": "AI-Powered Expiry Validation Backend is running.",
        "project": "AI-Powered Expiry Validation System",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "modules": [
            {
                "name": "Authentication",
                "prefix": "/api/v1/auth"
            },
            {
                "name": "OCR",
                "prefix": "/api/v1/ocr"
            },
            {
                "name": "Barcode",
                "prefix": "/api/v1/products"
            },
            {
                "name": "Inventory",
                "prefix": "/api/v1/inventory"
            },
            {
                "name": "Community Users",
                "prefix": "/api/v1/community/users"
            },
            {
                "name": "Community Reports",
                "prefix": "/api/v1/community/reports"
            },
            {
                "name": "Credibility Engine",
                "prefix": "/api/v1/community/credibility"
            },
            {
                "name": "Issue Clusters",
                "prefix": "/api/v1/community/clusters"
            },
            {
                "name": "Community Intelligence",
                "prefix": "/api/v1/community/intelligence"
            },
            {
                "name": "Safety Alerts",
                "prefix": "/api/v1/community/alerts"
            },
            {
                "name": "Investigation Cases",
                "prefix": "/api/v1/community/cases"
            }
        ]
    }