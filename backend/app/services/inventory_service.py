"""
services/inventory_service.py — Inventory Intake business logic.

Business flow for create_inventory_item():
  1. Resolve Product from barcode  → 404 if not found
  2. Load financial profile snapshot (Phase 2)
  3. Call evaluate_shelf_life()    → get status + remaining_days + reason
  4. Persist InventoryItem         → return saved record
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.financial_profile import ProductFinancialProfile
from app.schemas.inventory_schema import InventoryIntakeRequest
from app.services.shelf_life_service import evaluate_shelf_life
from app.utils.constants import ACCEPTED, PRIORITY_SALE, REJECTED, MANUAL_REVIEW, INVALID_DATE
from app.utils.exceptions import InventoryItemNotFoundError, ProductNotFoundError, InvalidPricingError


def create_inventory_item(db: Session, data: InventoryIntakeRequest) -> InventoryItem:
    """
    Run the full inventory intake workflow:
      barcode → product lookup → financial snapshots → shelf-life evaluation → persist.

    Raises:
        ProductNotFoundError — if no product matches the barcode.
        InvalidPricingError — if pricing constraint validations fail.
    """
    # Step 1: resolve product
    product = db.query(Product).filter(Product.barcode == data.barcode).first()
    if not product:
        raise ProductNotFoundError(f"No product found for barcode '{data.barcode}'")

    # Step 2: resolve and copy financial metadata (Phase 2)
    purchase_price = data.purchase_price
    mrp = data.mrp
    currency = "INR"
    supplier_return_allowed = None
    supplier_return_percent = None
    snapshot = None

    profile = db.query(ProductFinancialProfile).filter(ProductFinancialProfile.product_id == product.id).first()
    if profile:
        if purchase_price is None:
            purchase_price = profile.purchase_price
        if mrp is None:
            mrp = profile.mrp
        currency = profile.currency or "INR"
        supplier_return_allowed = profile.supplier_return_allowed
        supplier_return_percent = profile.supplier_return_percent

        dec_purchase_price = Decimal(str(purchase_price))
        dec_mrp = Decimal(str(mrp))

        if dec_purchase_price <= 0:
            raise InvalidPricingError("Purchase price must be greater than zero")
        if dec_mrp < dec_purchase_price:
            raise InvalidPricingError("MRP must be greater than or equal to purchase price")

        snapshot = {
            "purchase_price": f"{dec_purchase_price:.2f}",
            "mrp": f"{dec_mrp:.2f}",
            "profit_margin_percent": f"{profile.default_profit_margin_percent:.2f}",
            "currency": currency,
            "brand": product.sku.split("-")[0] if "-" in product.sku else "",
            "product_name": product.name,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "profile_version": 1
        }
    else:
        # If no profile, but user passed pricing overrides in intake data, we validate and save them
        if purchase_price is not None:
            dec_purchase_price = Decimal(str(purchase_price))
            dec_mrp = Decimal(str(mrp)) if mrp is not None else dec_purchase_price

            if dec_purchase_price <= 0:
                raise InvalidPricingError("Purchase price must be greater than zero")
            if dec_mrp < dec_purchase_price:
                raise InvalidPricingError("MRP must be greater than or equal to purchase price")

            snapshot = {
                "purchase_price": f"{dec_purchase_price:.2f}",
                "mrp": f"{dec_mrp:.2f}",
                "profit_margin_percent": "0.00",
                "currency": currency,
                "brand": product.sku.split("-")[0] if "-" in product.sku else "",
                "product_name": product.name,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "profile_version": 0
            }

    # Step 3: evaluate shelf life
    decision = evaluate_shelf_life(data.manufacturing_date, data.expiry_date)

    # Step 4: persist inventory record
    item = InventoryItem(
        product_id=product.id,
        batch_number=data.batch_number,
        manufacturing_date=data.manufacturing_date,
        expiry_date=data.expiry_date,
        remaining_days=decision["remaining_days"],
        status=decision["status"],
        decision_reason=decision["decision_reason"],
        # Financial columns
        quantity=data.quantity if data.quantity is not None else 1,
        purchase_price=purchase_price,
        mrp=mrp,
        currency=currency,
        supplier_return_allowed=supplier_return_allowed,
        supplier_return_percent=supplier_return_percent,
        financial_profile_snapshot=snapshot,
    )
    
    # Event-sync triggers calculate_inventory_cost automatically upon creation
    db.add(item)
    db.commit()
    db.refresh(item)

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
