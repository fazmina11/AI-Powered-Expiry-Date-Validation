"""
scripts/seed_south_indian_products.py — Insert real-world South Indian mock products into PostgreSQL.

Idempotent: running this multiple times is safe.
  - Existing records (matched by barcode OR sku) are skipped.
  - New records are inserted.
  - Final counts are printed for verification.

Usage:
    python scripts/seed_south_indian_products.py
"""

import sys
import os
import uuid
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.database import SessionLocal, check_db_connection
from app.models.product import Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── South Indian Products ─────────────────────────────────────────
PRODUCTS = [
    {
        "name":                 "MTR Rava Idli Mix 500g",
        "brand":                "MTR",
        "sku":                  "MTR-RAVA-IDLI-500G",
        "barcode":              "8901042953256",
        "barcode_type":         "EAN13",
        "category":             "Packaged Foods",
        "description":          "Ready to cook Rava Idli mix, a popular South Indian breakfast.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Sakthi Sambar Powder 200g",
        "brand":                "Sakthi Masala",
        "sku":                  "SAKTHI-SAMBAR-200G",
        "barcode":              "8906001020345",
        "barcode_type":         "EAN13",
        "category":             "Spices",
        "description":          "Authentic South Indian Sambar powder mix.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "GRB Udhayam Ghee 500ml",
        "brand":                "GRB",
        "sku":                  "GRB-GHEE-500ML",
        "barcode":              "8906008850020",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Pure cow ghee, traditionally made in South India.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Milky Mist Paneer 200g",
        "brand":                "Milky Mist",
        "sku":                  "MILKY-PANEER-200G",
        "barcode":              "8904083300057",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Fresh malai paneer cubes, 200g vacuum packed.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "Heritage Toned Milk 500ml",
        "brand":                "Heritage",
        "sku":                  "HERITAGE-MILK-500ML",
        "barcode":              "8901234567890",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Pasteurised toned milk, popular in AP and Telangana.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "Aashirvaad Select Atta 5kg",
        "brand":                "Aashirvaad",
        "sku":                  "AASH-ATTA-5KG",
        "barcode":              "8901725134185",
        "barcode_type":         "EAN13",
        "category":             "Packaged Foods",
        "description":          "100% MP Sharbati wheat atta, premium quality.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Bru Green Label Filter Coffee 500g",
        "brand":                "Bru",
        "sku":                  "BRU-FILTER-500G",
        "barcode":              "8901030018516",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "Traditional filter coffee powder with chicory blend.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Parachute Pure Coconut Oil 250ml",
        "brand":                "Parachute",
        "sku":                  "PARA-COCONUT-250ML",
        "barcode":              "8901088015036",
        "barcode_type":         "EAN13",
        "category":             "Personal Care",
        "description":          "100% pure unrefined coconut oil, popular in Kerala.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Narasu's Udhayam Filter Coffee 250g",
        "brand":                "Narasu's",
        "sku":                  "NARASU-COFFEE-250G",
        "barcode":              "8904000100159",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "Classic South Indian filter coffee blend.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Aachi Chicken Masala 200g",
        "brand":                "Aachi",
        "sku":                  "AACHI-CHICKEN-200G",
        "barcode":              "8906020580327",
        "barcode_type":         "EAN13",
        "category":             "Spices",
        "description":          "Authentic Chettinad style chicken masala.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Idhayam Sesame Oil 1L",
        "brand":                "Idhayam",
        "sku":                  "IDHAYAM-SESAME-1L",
        "barcode":              "8901243100021",
        "barcode_type":         "EAN13",
        "category":             "Cooking Oil",
        "description":          "Traditional gingelly (sesame) oil, extensively used in South Indian cooking.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Lion Dates 500g",
        "brand":                "Lion",
        "sku":                  "LION-DATES-500G",
        "barcode":              "8906001080011",
        "barcode_type":         "EAN13",
        "category":             "Dry Fruits",
        "description":          "High-quality seedless dates.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Anil Vermicelli (Semiya) 200g",
        "brand":                "Anil",
        "sku":                  "ANIL-SEMIYA-200G",
        "barcode":              "8904123400561",
        "barcode_type":         "EAN13",
        "category":             "Packaged Foods",
        "description":          "Roasted semiya for Payasam and Upma.",
        "default_storage_type": "ambient",
    },
    {
        "name":                 "Hatsun Curd 500g",
        "brand":                "Hatsun",
        "sku":                  "HATSUN-CURD-500G",
        "barcode":              "8906005541129",
        "barcode_type":         "EAN13",
        "category":             "Dairy",
        "description":          "Thick and tasty set curd.",
        "default_storage_type": "refrigerated",
    },
    {
        "name":                 "3 Roses Tea 500g",
        "brand":                "Brooke Bond",
        "sku":                  "3ROSES-TEA-500G",
        "barcode":              "8901030383744",
        "barcode_type":         "EAN13",
        "category":             "Beverages",
        "description":          "Strong tea dust blend favoured in Tamil Nadu.",
        "default_storage_type": "ambient",
    }
]

def main():
    try:
        if not check_db_connection():
            logger.error("Could not connect to the database. Exiting.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"check_db_connection threw an exception: {e}")
        sys.exit(1)

    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0

        for p_data in PRODUCTS:
            # Check if product exists by SKU or Barcode
            existing = db.query(Product).filter(
                (Product.sku == p_data["sku"]) | (Product.barcode == p_data["barcode"])
            ).first()

            if existing:
                logger.info(f"Skipping existing product: {p_data['name']} (SKU: {p_data['sku']})")
                skipped += 1
                continue

            # Create new product
            new_product = Product(
                id=uuid.uuid4(),
                name=p_data["name"],
                brand=p_data["brand"],
                sku=p_data["sku"],
                barcode=p_data["barcode"],
                barcode_type=p_data["barcode_type"],
                category=p_data["category"],
                description=p_data["description"],
                default_storage_type=p_data["default_storage_type"]
            )
            db.add(new_product)
            inserted += 1

        db.commit()
        logger.info(f"Successfully seeded South Indian products. Inserted: {inserted}, Skipped: {skipped}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
