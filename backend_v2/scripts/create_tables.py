import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, check_db_connection, engine
from app.models import (  # noqa: F401
    AuditLog,
    BarcodeScan,
    ExternalProductEnrichmentLog,
    InventoryItem,
    InventoryMovement,
    ManualReview,
    MLPrediction,
    OCRResult,
    Product,
    ProductAllergen,
    ProductIdentifier,
    ProductImage,
    ProductIngredient,
    ProductNutrition,
    ProductStorageRequirement,
    ScanAlert,
    ScanSession,
    StorageContext,
    StorageLocation,
    Supplier,
    Warehouse,
)


def main():
    print("Checking database connection...")
    if not check_db_connection():
        print("ERROR: Cannot connect to the database.")
        print("Make sure Docker is running: docker-compose up -d")
        sys.exit(1)

    print("Creating tables (IF NOT EXISTS)...")
    Base.metadata.create_all(bind=engine)

    table_names = sorted(Base.metadata.tables.keys())
    print(f"\n{len(table_names)} tables ready:")
    for name in table_names:
        print(f"   {name}")


if __name__ == "__main__":
    main()
