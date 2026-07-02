"""
main.py — Application entry point.

Phase 1.8: API versioning under /api/v1/*
           Enhanced health check
           Structured logging on startup
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.utils.logger import logger

# Register all models on Base.metadata before create_all
from app.models import product, inventory, validation_record  # noqa: F401

# Canonical routers (Phase 1.3 – 1.7)
from app.routes import auth
from app.routes.product_routes    import router as product_router
from app.routes.inventory_routes  import router as inventory_router
from app.routes.validation_routes import router as validation_router
from app.routes.dashboard_routes  import router as dashboard_router

APP_VERSION = "1.0.0"
API_PREFIX  = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: create tables in development mode.
    In production use Alembic: alembic upgrade head
    """
    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified / created (development mode)")
    logger.info("AI-Powered Expiry Validation API v%s started [%s]", APP_VERSION, settings.APP_ENV)
    yield
    logger.info("API shutting down")


app = FastAPI(
    title="AI-Powered Expiry Date Validation API",
    description="Backend for warehouse/dark-store product expiry validation.",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health check ──────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    """Enhanced health endpoint — checks DB connectivity."""
    from sqlalchemy import text
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    return {
        "status":   "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "version":  APP_VERSION,
        "env":      settings.APP_ENV,
    }

# ── Versioned routers  /api/v1/* ──────────────────────────────
app.include_router(auth.router,        prefix=f"{API_PREFIX}/auth",       tags=["auth"])
app.include_router(product_router,     prefix=f"{API_PREFIX}/products",   tags=["products"])
app.include_router(inventory_router,   prefix=f"{API_PREFIX}/inventory",  tags=["inventory"])
app.include_router(validation_router,  prefix=f"{API_PREFIX}/validation", tags=["validation"])
app.include_router(dashboard_router,   prefix=f"{API_PREFIX}/dashboard",  tags=["dashboard"])
