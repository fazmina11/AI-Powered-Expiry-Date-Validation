#!/usr/bin/env python
"""
scripts/backfill_inventory_financials.py — Backfill migration utility for Phase 2.
Updates legacy inventory items by attaching financial attributes from the
master ProductFinancialProfile, generating historical snapshots, and synchronizing cost.
"""

from datetime import datetime
from decimal import Decimal
import os
import sys

# Add parent directory to path to enable imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.financial_profile import ProductFinancialProfile


def main():
    db = SessionLocal()
    try:
        print("Starting inventory financials backfill migration...")
        
        # Query items missing financial snapshots or pricing values
        items_to_migrate = db.query(InventoryItem).filter(
            (InventoryItem.purchase_price == None) |
            (InventoryItem.mrp == None) |
            (InventoryItem.financial_profile_snapshot == None)
        ).all()

        total_found = len(items_to_migrate)
        print(f"Found {total_found} inventory items needing migration.")

        migrated_count = 0
        skipped_no_profile_count = 0

        for item in items_to_migrate:
            # 1. Resolve product and profile
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                print(f"Warning: Product not found for inventory item ID {item.id}. Skipping.")
                continue

            profile = db.query(ProductFinancialProfile).filter(
                ProductFinancialProfile.product_id == product.id
            ).first()

            if not profile:
                print(f"Warning: No financial profile found for product '{product.name}' (ID: {product.id}). Skipping.")
                skipped_no_profile_count += 1
                continue

            # 2. Populate values using Decimal arithmetic
            item.purchase_price = profile.purchase_price
            item.mrp = profile.mrp
            item.currency = profile.currency or "INR"
            item.supplier_return_allowed = profile.supplier_return_allowed
            item.supplier_return_percent = profile.supplier_return_percent

            # Sync quantity (default to 1 if null)
            qty = item.quantity if item.quantity is not None else 1
            item.quantity = qty
            
            # calculate_inventory_cost triggers validates event automatically
            item.inventory_cost = Decimal(str(qty)) * Decimal(str(profile.purchase_price))

            # 3. Build string-serialized snapshot
            item.financial_profile_snapshot = {
                "purchase_price": f"{profile.purchase_price:.2f}",
                "mrp": f"{profile.mrp:.2f}",
                "profit_margin_percent": f"{profile.default_profit_margin_percent:.2f}",
                "currency": item.currency,
                "brand": product.sku.split("-")[0] if "-" in product.sku else "",
                "product_name": product.name,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "profile_version": 1
            }

            migrated_count += 1

        if migrated_count > 0:
            db.commit()
            print(f"Migration completed successfully. Migrated: {migrated_count} items. Skipped (missing profile): {skipped_no_profile_count} items.")
        else:
            print("No items were migrated.")

    except Exception as e:
        db.rollback()
        print(f"Error executing backfill migration: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
