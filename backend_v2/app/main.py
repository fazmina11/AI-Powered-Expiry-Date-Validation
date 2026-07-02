"""
main.py — Phase 2 FastAPI application entry point.

Routes will be added in upcoming phases.
This file establishes the app, health check, and DB connectivity probe.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_db_connection

# Register all models on Base.metadata
from app.models import (  # noqa: F401
    Product, ProductIdentifier, ProductIngredient, ProductAllergen,
    ProductNutrition, ProductStorageRequirement, Supplier, Warehouse,
    StorageLocation, ScanSession, BarcodeScan, ProductImage, OCRResult,
    InventoryItem, InventoryMovement, ManualReview, ScanAlert, AuditLog,
    ExternalProductEnrichmentLog, StorageContext, MLPrediction,
)
from app.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ok = check_db_connection()
    status = "connected" if db_ok else "UNAVAILABLE"
    print(f"[startup] database: {status} | env: {settings.APP_ENV} | v{settings.APP_VERSION}")
    yield


app = FastAPI(
    title="AI-Powered Expiry Validation API — Phase 2",
    description="Backend MVP: product catalogue, barcode scanning, OCR pipeline preparation, ML handoff.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)


@app.get("/health", tags=["health"])
def health_check():
    db_ok = check_db_connection()
    return {
        "status":   "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "version":  settings.APP_VERSION,
        "env":      settings.APP_ENV,
    }
