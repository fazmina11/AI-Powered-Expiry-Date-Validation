"""
main.py — Application entry point.

Phase 2.0 — AUTH-FREE DEVELOPMENT MODE
---------------------------------------
Authentication has been temporarily removed to allow independent
development of all business APIs.

Authentication will be re-introduced using Firebase Admin SDK.
Preserved auth code lives in: app/legacy/auth/

Active routers (all public, no auth required):
  /api/v1/products/*   → product_routes.py
  /api/v1/inventory/*  → inventory_routes.py
  /api/v1/validation/* → validation_routes.py
  /api/v1/dashboard/*  → dashboard_routes.py

Swagger is completely open — no Authorization header required.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.utils.logger import logger

# ── Model registration (users table preserved for Firebase re-integration) ──
# NOTE: User model is imported so the users table is NOT dropped from the DB.
# It will be reused when Firebase UID mapping is implemented.
from app.models import product, inventory, validation_record, financial_profile, warehouse  # noqa: F401
from app.models.user import User  # noqa: F401  — preserves users table

# ── Business routers (auth router intentionally excluded) ───────────────────
from app.routes.product_routes    import router as product_router
from app.routes.inventory_routes  import router as inventory_router
from app.routes.validation_routes import router as validation_router
from app.routes.dashboard_routes  import router as dashboard_router
from app.routes.financial_profile_routes import router as financial_profile_router
from app.routes.warehouse_routes  import router as warehouse_router
from app.routes.assistant_routes  import router as assistant_router

APP_VERSION = "2.0.0-dev-noauth"
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
    logger.info(
        "AI-Powered Expiry Validation API v%s started [%s] — AUTH-FREE MODE",
        APP_VERSION, settings.APP_ENV,
    )
    yield
    logger.info("API shutting down")


# ── FastAPI app — no security scheme, no OAuth2 ─────────────────────────────
app = FastAPI(
    title="AI-Powered Expiry Date Validation API",
    description=(
        "Backend for warehouse/dark-store product expiry validation.\n\n"
        "**Development Mode — Authentication Disabled**\n"
        "All endpoints are publicly accessible. "
        "Firebase authentication will be added in a future phase."
    ),
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    # Explicitly no swagger_ui_oauth2_redirect_url or security schemes
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    """Health endpoint — checks DB connectivity."""
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
        "auth":     "disabled — Firebase re-integration pending",
    }


# ── Business API routers (/api/v1/*) ─────────────────────────────────────────
# Auth router intentionally excluded. Preserved in: app/legacy/auth/
app.include_router(product_router,     prefix=f"{API_PREFIX}/products",   tags=["products"])
app.include_router(inventory_router,   prefix=f"{API_PREFIX}/inventory",  tags=["inventory"])
app.include_router(validation_router,  prefix=f"{API_PREFIX}/validation", tags=["validation"])
app.include_router(dashboard_router,   prefix=f"{API_PREFIX}/dashboard",  tags=["dashboard"])
app.include_router(financial_profile_router, prefix=f"{API_PREFIX}/financial-profiles", tags=["financial-profiles"])
app.include_router(warehouse_router,   prefix=f"{API_PREFIX}/warehouse-intelligence", tags=["warehouse-intelligence"])
app.include_router(assistant_router,   prefix=f"{API_PREFIX}/assistant",  tags=["assistant"])
