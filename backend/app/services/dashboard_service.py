"""
services/dashboard_service.py — All aggregation logic for dashboard endpoints.

No business decisions here — only read queries and count aggregations.
All aggregation stays in the service layer; routes stay thin.
"""

from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.validation_record import ValidationRecord
from app.schemas.dashboard_schema import (
    AlertsResponse,
    DashboardSummaryResponse,
    InventoryBreakdownResponse,
    ValidationBreakdownResponse,
)
from app.utils.constants import (
    ACCEPTED,
    INVALID_DATE,
    LOW_CONFIDENCE,
    MANUAL_REVIEW,
    PRIORITY_SALE,
    REJECTED,
    VALID,
)

# Statuses that need human attention
ALERT_STATUSES = {REJECTED, INVALID_DATE, MANUAL_REVIEW}


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    """Return a full summary of products, inventory, and validation counts."""
    return DashboardSummaryResponse(
        total_products=db.query(Product).count(),
        total_inventory_items=db.query(InventoryItem).count(),
        accepted_count=db.query(InventoryItem).filter(InventoryItem.status == ACCEPTED).count(),
        priority_sale_count=db.query(InventoryItem).filter(InventoryItem.status == PRIORITY_SALE).count(),
        rejected_count=db.query(InventoryItem).filter(InventoryItem.status == REJECTED).count(),
        manual_review_count=db.query(InventoryItem).filter(InventoryItem.status == MANUAL_REVIEW).count(),
        invalid_date_count=db.query(InventoryItem).filter(InventoryItem.status == INVALID_DATE).count(),
        valid_validation_count=db.query(ValidationRecord).filter(ValidationRecord.validation_status == VALID).count(),
        low_confidence_count=db.query(ValidationRecord).filter(ValidationRecord.validation_status == LOW_CONFIDENCE).count(),
    )


def get_inventory_breakdown(db: Session) -> InventoryBreakdownResponse:
    """Return per-status counts for inventory items."""
    return InventoryBreakdownResponse(
        accepted=db.query(InventoryItem).filter(InventoryItem.status == ACCEPTED).count(),
        priority_sale=db.query(InventoryItem).filter(InventoryItem.status == PRIORITY_SALE).count(),
        rejected=db.query(InventoryItem).filter(InventoryItem.status == REJECTED).count(),
        manual_review=db.query(InventoryItem).filter(InventoryItem.status == MANUAL_REVIEW).count(),
        invalid_date=db.query(InventoryItem).filter(InventoryItem.status == INVALID_DATE).count(),
    )


def get_validation_breakdown(db: Session) -> ValidationBreakdownResponse:
    """Return per-status counts for validation records."""
    return ValidationBreakdownResponse(
        valid=db.query(ValidationRecord).filter(ValidationRecord.validation_status == VALID).count(),
        low_confidence=db.query(ValidationRecord).filter(ValidationRecord.validation_status == LOW_CONFIDENCE).count(),
        manual_review=db.query(ValidationRecord).filter(ValidationRecord.validation_status == MANUAL_REVIEW).count(),
    )


def get_recent_inventory(db: Session, limit: int = 10) -> list[InventoryItem]:
    """Return the most recently created inventory items, newest first."""
    return (
        db.query(InventoryItem)
        .order_by(InventoryItem.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_validations(db: Session, limit: int = 10) -> list[ValidationRecord]:
    """Return the most recently created validation records, newest first."""
    return (
        db.query(ValidationRecord)
        .order_by(ValidationRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def get_alerts(db: Session) -> AlertsResponse:
    """
    Return all inventory items that need attention:
    REJECTED, INVALID_DATE, or MANUAL_REVIEW.
    Ordered newest first.
    """
    items = (
        db.query(InventoryItem)
        .filter(InventoryItem.status.in_(ALERT_STATUSES))
        .order_by(InventoryItem.created_at.desc())
        .all()
    )
    return AlertsResponse(count=len(items), items=items)
