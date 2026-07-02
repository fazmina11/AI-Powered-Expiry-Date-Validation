"""
services/inventory_service.py — Inventory Intake business logic.

Business flow for create_inventory_item():
  1. Resolve Product from barcode  → 404 if not found
  2. Call evaluate_shelf_life()    → get status + remaining_days + reason
  3. Persist InventoryItem         → return saved record

All other functions are thin query helpers used by routes.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.schemas.inventory_schema import InventoryIntakeRequest
from app.services.shelf_life_service import evaluate_shelf_life
from app.utils.constants import ACCEPTED, PRIORITY_SALE, REJECTED, MANUAL_REVIEW, INVALID_DATE
from app.utils.exceptions import InventoryItemNotFoundError, ProductNotFoundError


# ── Phase 1.5 canonical function names ───────────────────────

def create_inventory_item(db: Session, data: InventoryIntakeRequest) -> InventoryItem:
    """
    Run the full inventory intake workflow:
      barcode → product lookup → shelf-life evaluation → persist → return.

    Raises:
        ProductNotFoundError — if no product matches the barcode.
    """
    # Step 1: resolve product
    product = db.query(Product).filter(Product.barcode == data.barcode).first()
    if not product:
        raise ProductNotFoundError(f"No product found for barcode '{data.barcode}'")

    # Step 2: evaluate shelf life
    decision = evaluate_shelf_life(data.manufacturing_date, data.expiry_date)

    # Step 3: persist inventory record
    item = InventoryItem(
        product_id=product.id,
        batch_number=data.batch_number,
        manufacturing_date=data.manufacturing_date,
        expiry_date=data.expiry_date,
        remaining_days=decision["remaining_days"],
        status=decision["status"],
        decision_reason=decision["decision_reason"],
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # Step 4: return
    return item


def get_inventory_by_id(db: Session, item_id: int) -> InventoryItem:
    """
    Return the InventoryItem with the given ID.
    Raises InventoryItemNotFoundError if not found.
    """
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise InventoryItemNotFoundError(f"Inventory item {item_id} not found")
    return item


def get_all_inventory(
    db: Session, skip: int = 0, limit: int = 50
) -> tuple[int, list[InventoryItem]]:
    """
    Return (total_count, paginated_items) for all inventory records.
    """
    query = db.query(InventoryItem)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items


def get_inventory_by_status(
    db: Session, status: str, skip: int = 0, limit: int = 50
) -> tuple[int, list[InventoryItem]]:
    """
    Return (total_count, paginated_items) filtered by status.
    """
    query = db.query(InventoryItem).filter(InventoryItem.status == status)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items


# ── Backward-compatible aliases (used by existing tests) ─────

def intake(db: Session, data: InventoryIntakeRequest) -> InventoryItem:
    """Alias for create_inventory_item() — keeps existing tests passing."""
    return create_inventory_item(db, data)


def get_item(db: Session, item_id: int) -> Optional[InventoryItem]:
    """Alias for get_inventory_by_id() — returns None instead of raising."""
    return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()


def list_items(
    db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 50
) -> list[InventoryItem]:
    """Alias — returns a flat list, used by existing tests and dashboard."""
    query = db.query(InventoryItem)
    if status:
        query = query.filter(InventoryItem.status == status)
    return query.offset(skip).limit(limit).all()


def get_dashboard_summary(db: Session) -> dict:
    """Return counts per status for the dashboard endpoint."""
    return {
        "total":        db.query(InventoryItem).count(),
        "accepted":     db.query(InventoryItem).filter(InventoryItem.status == ACCEPTED).count(),
        "priority_sale":db.query(InventoryItem).filter(InventoryItem.status == PRIORITY_SALE).count(),
        "rejected":     db.query(InventoryItem).filter(InventoryItem.status == REJECTED).count(),
        "manual_review":db.query(InventoryItem).filter(InventoryItem.status == MANUAL_REVIEW).count(),
        "invalid_date": db.query(InventoryItem).filter(InventoryItem.status == INVALID_DATE).count(),
    }
