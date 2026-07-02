"""
routes/dashboard_routes.py — Dashboard & Monitoring API endpoints.

Phase 1.7 canonical router.

All aggregation logic lives in dashboard_service.py.
Routes only handle HTTP concerns.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard_schema import (
    AlertItem,
    RecentInventoryItem,
    RecentValidationItem,
)
from app.services.dashboard_service import (
    get_alerts,
    get_dashboard_summary,
    get_inventory_breakdown,
    get_recent_inventory,
    get_recent_validations,
    get_validation_breakdown,
)
from app.utils.response import success_response

router = APIRouter()


# ── GET /dashboard/summary ────────────────────────────────────

@router.get("/summary")
def summary_endpoint(db: Session = Depends(get_db)):
    """
    Full dashboard summary:
    product count, inventory counts by status, validation counts by status.
    """
    data = get_dashboard_summary(db)
    return success_response(data=data, message="Dashboard summary retrieved")


# ── GET /dashboard/inventory-breakdown ───────────────────────

@router.get("/inventory-breakdown")
def inventory_breakdown_endpoint(db: Session = Depends(get_db)):
    """Inventory item counts grouped by decision status."""
    data = get_inventory_breakdown(db)
    return success_response(data=data, message="Inventory breakdown retrieved")


# ── GET /dashboard/validation-breakdown ──────────────────────

@router.get("/validation-breakdown")
def validation_breakdown_endpoint(db: Session = Depends(get_db)):
    """Validation record counts grouped by validation status."""
    data = get_validation_breakdown(db)
    return success_response(data=data, message="Validation breakdown retrieved")


# ── GET /dashboard/recent-inventory ──────────────────────────

@router.get("/recent-inventory")
def recent_inventory_endpoint(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return the most recently created inventory items, newest first."""
    items = get_recent_inventory(db, limit=limit)
    return success_response(
        data=[RecentInventoryItem.model_validate(i) for i in items],
        message="Recent inventory retrieved",
    )


# ── GET /dashboard/recent-validations ────────────────────────

@router.get("/recent-validations")
def recent_validations_endpoint(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return the most recently created validation records, newest first."""
    records = get_recent_validations(db, limit=limit)
    return success_response(
        data=[RecentValidationItem.model_validate(r) for r in records],
        message="Recent validations retrieved",
    )


# ── GET /dashboard/alerts ─────────────────────────────────────

@router.get("/alerts")
def alerts_endpoint(db: Session = Depends(get_db)):
    """
    Return all inventory items needing attention:
    REJECTED, INVALID_DATE, MANUAL_REVIEW.
    """
    result = get_alerts(db)
    return success_response(
        data={
            "count": result.count,
            "items": [AlertItem.model_validate(i) for i in result.items],
        },
        message="Alerts retrieved",
    )
