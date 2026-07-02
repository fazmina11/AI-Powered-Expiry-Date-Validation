"""
scripts/seed_products.py — Insert 20 realistic mock products into PostgreSQL.

Idempotent: running this multiple times is safe.
  - Existing records (matched by barcode OR sku) are skipped.
  - New records are inserted.
  - Final counts are printed for verification.

Usage:
    python scripts/seed_products.py

Categories covered:
  Dairy · Beverages · Snacks · Bakery · Personal Care · Packaged Foods
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, check_db_connection
from app.models.product import Product

# ── 20 Mock Products ──────────────────────────────────────────
# Fields: name, brand, sku, barcode, barcode_type, category,
#         description, default_storage_type
PRODUCTS = [
    # ── Dairy ─────────────────────────────────────────────────
    {
        "name":                 "Full Cream Milk 1L",
        "brand":                "Amul",
        "sku":                  "AMUL-MILK-1L",
        "barcode":              "8901058000027",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Pasteurised full cream milk in a 1-litre tetra pack.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "Low Fat Yogurt 400g",
        "brand":                "Nestle",
        "sku":                  "NESTLE-YOG-400G",
        "barcode":              "8901030789010",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Low-fat plain yogurt with live cultures, 400g tub.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "Processed Cheese Slices 200g",
        "brand":                "Britannia",
        "sku":                  "BRIT-CHEESE-200G",
        "barcode":              "8901063150245",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Individually wrapped processed cheese slices, 200g pack.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "Salted Butter 100g",
        "brand":                "Mother Dairy",
        "sku":                  "MDAIRY-BUT-100G",
        "barcode":              "8904117100018",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Creamy salted butter, 100g block.",
        "default_storage_type": "refrigerated",
    },

    # ── Beverages ─────────────────────────────────────────────
    {
        "name":                 "Mango Fruit Drink 200ml",
        "brand":                "Frooti",
        "sku":                  "FROOTI-MANGO-200ML",
        "barcode":              "8901088100015",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "Mango flavoured fruit drink, 200ml tetra pack.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Orange Juice 1L",
        "brand":                "Tropicana",
        "sku":                  "TROP-OJ-1L",
        "barcode":              "0012000001086",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "100% pure pressed orange juice, 1-litre carton.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "Green Tea 25 Bags",
        "brand":                "Tetley",
        "sku":                  "TETLEY-GT-25",
        "barcode":              "0055100150002",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "Green tea bags, pack of 25. Store in cool dry place.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Sparkling Mineral Water 500ml",
        "brand":                "Perrier",
        "sku":                  "PERRIER-500ML",
        "barcode":              "0074780300018",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "Naturally sparkling mineral water, 500ml glass bottle.",
        "default_storage_type": "ambient",
    },

    # ── Snacks ────────────────────────────────────────────────
    {
        "name":                 "Classic Salted Chips 100g",
        "brand":                "Lays",
        "sku":                  "LAYS-SALT-100G",
        "barcode":              "0028400589758",
        "barcode_type":         "EAN13",
        "category":             "Snacks",
        "description":          "Classic salted potato chips, 100g bag.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Dark Chocolate Bar 80g",
        "brand":                "Cadbury Bournville",
        "sku":                  "CAD-BORN-80G",
        "barcode":              "7622300441937",
        "barcode_type":         "EAN13",
        "category":             "Snacks",
        "description":          "Rich dark chocolate 70% cocoa, 80g bar.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Roasted Mixed Nuts 150g",
        "brand":                "Happilo",
        "sku":                  "HAPPI-MNUTS-150G",
        "barcode":              "8906017260093",
        "barcode_type":         "EAN13",
        "category":             "Snacks",
        "description":          "Dry roasted mixed nuts — almonds, cashews, walnuts, 150g.",
        "default_storage_type": "ambient",
    },

    # ── Bakery ────────────────────────────────────────────────
    {
        "name":                 "Whole Wheat Bread 400g",
        "brand":                "Harvest Gold",
        "sku":                  "HG-WWBREAD-400G",
        "barcode":              "8906068110018",
        "barcode_type":         "EAN13",
        "category":             "Bakery",
        "description":          "Whole wheat sandwich bread, 400g loaf (18 slices).",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Butter Croissant 6-Pack",
        "brand":                "Monginis",
        "sku":                  "MONG-CROIS-6PK",
        "barcode":              "8904265100012",
        "barcode_type":         "EAN13",
        "category":             "Bakery",
        "description":          "Freshly baked all-butter croissants, pack of 6.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Digestive Biscuits 400g",
        "brand":                "McVitie's",
        "sku":                  "MCVIT-DIG-400G",
        "barcode":              "5000168003009",
        "barcode_type":         "EAN13",
        "category":             "Bakery",
        "description":          "Original digestive wheat biscuits, 400g pack.",
        "default_storage_type": "ambient",
    },

    # ── Personal Care ─────────────────────────────────────────
    {
        "name":                 "Moisturising Shampoo 340ml",
        "brand":                "Dove",
        "sku":                  "DOVE-SHAMP-340ML",
        "barcode":              "0011111019220",
        "barcode_type":         "EAN13",
        "category":             "Personal Care",
        "description":          "Intensive moisture repair shampoo for dry hair, 340ml.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Sunscreen SPF 50 100ml",
        "brand":                "Lotus Herbals",
        "sku":                  "LOTUS-SPF50-100ML",
        "barcode":              "8901176011339",
        "barcode_type":         "EAN13",
        "category":             "Personal Care",
        "description":          "Broad spectrum SPF 50 sunscreen, 100ml tube.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Toothpaste Whitening 150g",
        "brand":                "Colgate",
        "sku":                  "COLG-WHITE-150G",
        "barcode":              "0035000138637",
        "barcode_type":         "EAN13",
        "category":             "Personal Care",
        "description":          "Advanced whitening toothpaste with fluoride, 150g.",
        "default_storage_type": "ambient",
    },

    # ── Packaged Foods ────────────────────────────────────────
    {
        "name":                 "Basmati Rice 5kg",
        "brand":                "India Gate",
        "sku":                  "IGATE-BASMATI-5KG",
        "barcode":              "8906000940019",
        "barcode_type":         "EAN13",
        "category":             "Packaged Foods",
        "description":          "Premium aged basmati rice, 5kg vacuum-sealed bag.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Masala Instant Noodles 70g",
        "brand":                "Maggi",
        "sku":                  "MAGGI-MASALA-70G",
        "barcode":              "8901058504121",
        "barcode_type":         "EAN13",
        "category":             "Packaged Foods",
        "description":          "Instant noodles with masala tastemaker, 70g single serving.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Frozen Peas 500g",
        "brand":                "McCain",
        "sku":                  "MCCAIN-PEAS-500G",
        "barcode":              "0065251000188",
        "barcode_type":         "EAN13",
        "category":             "Packaged Foods",
        "description":          "Garden fresh frozen green peas, 500g resealable bag.",
        "default_storage_type": "frozen",
    },
]


def seed():
    print("Checking database connection...")
    if not check_db_connection():
        print("ERROR: Cannot connect to PostgreSQL.")
        print("Start Docker first:  docker-compose up -d")
        sys.exit(1)

    db = SessionLocal()
    inserted = 0
    skipped  = 0

    try:
        for data in PRODUCTS:
            # ── Idempotency check — skip if barcode OR sku already exists ──
            existing = (
                db.query(Product)
                .filter(
                    (Product.barcode == data["barcode"]) |
                    (Product.sku     == data["sku"])
                )
                .first()
            )

            if existing:
                skipped += 1
                print(f"  SKIP  {data['sku']:30s} (barcode or SKU already exists)")
                continue

            product = Product(
                id                   = uuid.uuid4(),
                name                 = data["name"],
                brand                = data["brand"],
                sku                  = data["sku"],
                barcode              = data["barcode"],
                barcode_type         = data["barcode_type"],
                category             = data["category"],
                description          = data["description"],
                default_storage_type = data["default_storage_type"],
                is_active            = True,
            )
            db.add(product)
            inserted += 1
            print(f"  INSERT {data['sku']:30s} ({data['category']})")

        db.commit()

    except Exception as exc:
        db.rollback()
        print(f"\nERROR during seed: {exc}")
        sys.exit(1)
    finally:
        db.close()

    print(f"\n{'─'*55}")
    print(f"  Inserted : {inserted}")
    print(f"  Skipped  : {skipped}")
    print(f"  Total    : {inserted + skipped} / {len(PRODUCTS)}")
    print(f"{'─'*55}")
    print("\n✅ Seed complete. Run the verification query to confirm:")
    print("   python scripts/verify_products.py")


if __name__ == "__main__":
    seed()
