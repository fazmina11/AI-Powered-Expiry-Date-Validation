"""
scripts/verify_products.py — Confirm seeded products are in the database.

Prints a formatted table and per-category summary.

Usage:
    python scripts/verify_products.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import func
from app.database import SessionLocal, check_db_connection
from app.models.product import Product


def verify():
    if not check_db_connection():
        print("ERROR: Cannot connect to the database.")
        sys.exit(1)

    db = SessionLocal()
    try:
        products = db.query(Product).order_by(Product.category, Product.name).all()
        total    = len(products)

        print(f"\n{'─'*90}")
        print(f"  {'NAME':<35} {'SKU':<22} {'BARCODE':<15} {'CATEGORY':<16} {'STORAGE'}")
        print(f"{'─'*90}")

        for p in products:
            print(
                f"  {p.name:<35} {p.sku:<22} {p.barcode:<15} "
                f"{(p.category or ''):<16} {p.default_storage_type or ''}"
            )

        print(f"{'─'*90}")
        print(f"  Total records: {total}\n")

        # Per-category counts
        counts = (
            db.query(Product.category, func.count(Product.id).label("cnt"))
            .group_by(Product.category)
            .order_by(Product.category)
            .all()
        )
        print("  By category:")
        for cat, cnt in counts:
            print(f"    {(cat or 'Unknown'):<20} {cnt}")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    verify()
