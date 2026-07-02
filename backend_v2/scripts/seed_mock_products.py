import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://expiry_user:expiry_password@localhost:5432/expiry_validation",
)

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    brand = Column(String(150), nullable=True)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    barcode = Column(String(100), nullable=False, unique=True, index=True)
    barcode_type = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    default_storage_type = Column(String(50), nullable=True)
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    barcode_scans = relationship("BarcodeScan", back_populates="product")
    product_images = relationship("ProductImage", back_populates="product")
    ocr_results = relationship("OCRResult", back_populates="product")
    inventory_items = relationship("InventoryItem", back_populates="product")


class BarcodeScan(Base):
    __tablename__ = "barcode_scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    barcode_value = Column(String(100), nullable=False, index=True)
    barcode_type = Column(String(50), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    scan_source = Column(String(50), nullable=False, default="laptop_camera")
    scan_status = Column(String(50), nullable=False)
    failure_reason = Column(Text, nullable=True)
    scanned_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    product = relationship("Product", back_populates="barcode_scans")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    barcode_scan_id = Column(UUID(as_uuid=True), ForeignKey("barcode_scans.id"), nullable=True)
    image_type = Column(String(50), nullable=False, default="LABEL")
    image_path = Column(Text, nullable=False)
    original_filename = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    captured_source = Column(String(50), nullable=False, default="laptop_camera")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    product = relationship("Product", back_populates="product_images")
    ocr_result = relationship("OCRResult", back_populates="product_image", uselist=False)


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_image_id = Column(UUID(as_uuid=True), ForeignKey("product_images.id"), nullable=False)
    raw_text = Column(Text, nullable=True)
    ocr_engine = Column(String(50), nullable=True)
    ocr_confidence = Column(Numeric(5, 4), nullable=True)
    candidate_mfg_date = Column(Date, nullable=True)
    candidate_expiry_date = Column(Date, nullable=True)
    candidate_packed_date = Column(Date, nullable=True)
    best_before_text = Column(String(255), nullable=True)
    batch_number_detected = Column(String(100), nullable=True)
    mrp_detected = Column(Numeric(10, 2), nullable=True)
    date_parse_confidence = Column(Numeric(5, 4), nullable=True)
    ocr_status = Column(String(50), nullable=False, default="PENDING")
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    product = relationship("Product", back_populates="ocr_results")
    product_image = relationship("ProductImage", back_populates="ocr_result")
    inventory_item = relationship("InventoryItem", back_populates="ocr_result", uselist=False)


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    ocr_result_id = Column(UUID(as_uuid=True), ForeignKey("ocr_results.id"), nullable=True)
    batch_number = Column(String(100), nullable=True, index=True)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    packed_date = Column(Date, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    intake_source = Column(String(50), nullable=False, default="OCR_SCAN")
    intake_status = Column(String(50), nullable=False, default="PENDING_ML_REVIEW")
    storage_location = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    product = relationship("Product", back_populates="inventory_items")
    ocr_result = relationship("OCRResult", back_populates="inventory_item")
    storage_contexts = relationship("StorageContext", back_populates="inventory_item")
    ml_predictions = relationship("MLPrediction", back_populates="inventory_item")
    manual_reviews = relationship("ManualReview", back_populates="inventory_item")


class StorageContext(Base):
    __tablename__ = "storage_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    storage_type = Column(String(50), nullable=True)
    storage_location = Column(String(150), nullable=True)
    temperature_celsius = Column(Numeric(5, 2), nullable=True)
    humidity_percent = Column(Numeric(5, 2), nullable=True)
    climate_source = Column(String(50), nullable=False, default="MANUAL")
    captured_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    inventory_item = relationship("InventoryItem", back_populates="storage_contexts")


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    predicted_remaining_life_days = Column(Integer, nullable=True)
    risk_level = Column(String(50), nullable=True)
    climate_risk = Column(String(50), nullable=True)
    priority_score = Column(Numeric(5, 2), nullable=True)
    recommended_action = Column(String(100), nullable=True)
    final_decision = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    confidence_score = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    inventory_item = relationship("InventoryItem", back_populates="ml_predictions")


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=True)
    ocr_result_id = Column(UUID(as_uuid=True), ForeignKey("ocr_results.id"), nullable=True)
    review_type = Column(String(50), nullable=False)
    corrected_mfg_date = Column(Date, nullable=True)
    corrected_expiry_date = Column(Date, nullable=True)
    corrected_batch_number = Column(String(100), nullable=True)
    reviewer_note = Column(Text, nullable=True)
    review_status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    inventory_item = relationship("InventoryItem", back_populates="manual_reviews")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


MOCK_PRODUCTS = [
    {"name": "Amul Taaza Toned Milk 500ml", "brand": "Amul", "sku": "AMUL-MILK-500ML", "barcode": "8901262010011", "barcode_type": "EAN13", "category": "Dairy", "description": "Pasteurized toned milk pouch for daily consumption.", "default_storage_type": "COLD", "image_url": None},
    {"name": "Nestle Everyday Dairy Whitener 400g", "brand": "Nestle", "sku": "NESTLE-EVERYDAY-400G", "barcode": "8901058850123", "barcode_type": "EAN13", "category": "Dairy", "description": "Dairy whitener powder for tea and coffee.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Britannia Good Day Cashew Cookies 200g", "brand": "Britannia", "sku": "BRIT-GD-CASHEW-200G", "barcode": "8901063160012", "barcode_type": "EAN13", "category": "Snacks", "description": "Cashew-flavored cookies packed for retail sale.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Parle-G Original Glucose Biscuits 250g", "brand": "Parle", "sku": "PARLE-G-250G", "barcode": "8901719101015", "barcode_type": "EAN13", "category": "Snacks", "description": "Glucose biscuits suitable for general consumption.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Lay's Classic Salted Chips 52g", "brand": "Lay's", "sku": "LAYS-CLASSIC-52G", "barcode": "8901491100226", "barcode_type": "EAN13", "category": "Snacks", "description": "Classic salted potato chips.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Kurkure Masala Munch 90g", "brand": "Kurkure", "sku": "KURKURE-MASALA-90G", "barcode": "8901491501221", "barcode_type": "EAN13", "category": "Snacks", "description": "Spicy crunchy corn-based snack.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Coca-Cola Original Taste 750ml", "brand": "Coca-Cola", "sku": "COKE-ORIGINAL-750ML", "barcode": "8901764012342", "barcode_type": "EAN13", "category": "Beverages", "description": "Carbonated soft drink bottle.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Real Mixed Fruit Juice 1L", "brand": "Real", "sku": "REAL-MIXED-FRUIT-1L", "barcode": "8901207011123", "barcode_type": "EAN13", "category": "Beverages", "description": "Packaged mixed fruit juice carton.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Tropicana Orange Delight 1L", "brand": "Tropicana", "sku": "TROP-ORANGE-1L", "barcode": "8901491200452", "barcode_type": "EAN13", "category": "Beverages", "description": "Packaged orange fruit beverage.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Mother Dairy Classic Curd 400g", "brand": "Mother Dairy", "sku": "MD-CURD-400G", "barcode": "8901648004321", "barcode_type": "EAN13", "category": "Dairy", "description": "Fresh curd pack requiring cold storage.", "default_storage_type": "COLD", "image_url": None},
    {"name": "Harvest Gold White Bread 400g", "brand": "Harvest Gold", "sku": "HG-WHITE-BREAD-400G", "barcode": "8901725180089", "barcode_type": "EAN13", "category": "Bakery", "description": "Packaged white bread loaf.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Britannia Brown Bread 400g", "brand": "Britannia", "sku": "BRIT-BROWN-BREAD-400G", "barcode": "8901063019870", "barcode_type": "EAN13", "category": "Bakery", "description": "Packaged brown bread loaf.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Maggi 2-Minute Noodles Masala 70g", "brand": "Maggi", "sku": "MAGGI-MASALA-70G", "barcode": "8901058840018", "barcode_type": "EAN13", "category": "Packaged Foods", "description": "Instant noodles with masala tastemaker.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Aashirvaad Whole Wheat Atta 1kg", "brand": "Aashirvaad", "sku": "AASHIRVAAD-ATTA-1KG", "barcode": "8901725123456", "barcode_type": "EAN13", "category": "Packaged Foods", "description": "Whole wheat flour pack.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Tata Salt Iodized 1kg", "brand": "Tata", "sku": "TATA-SALT-1KG", "barcode": "8904043901017", "barcode_type": "EAN13", "category": "Packaged Foods", "description": "Iodized salt packet.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Fortune Sunflower Oil 1L", "brand": "Fortune", "sku": "FORTUNE-SUNFLOWER-1L", "barcode": "8906007280012", "barcode_type": "EAN13", "category": "Packaged Foods", "description": "Refined sunflower cooking oil pouch.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Dove Cream Beauty Bathing Bar 100g", "brand": "Dove", "sku": "DOVE-BAR-100G", "barcode": "8901030865432", "barcode_type": "EAN13", "category": "Personal Care", "description": "Moisturizing bathing soap bar.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Colgate Strong Teeth Toothpaste 100g", "brand": "Colgate", "sku": "COLGATE-STRONG-100G", "barcode": "8901314010012", "barcode_type": "EAN13", "category": "Personal Care", "description": "Fluoride toothpaste for daily oral care.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Himalaya Baby Lotion 200ml", "brand": "Himalaya", "sku": "HIMALAYA-BABY-LOTION-200ML", "barcode": "8901138500782", "barcode_type": "EAN13", "category": "Personal Care", "description": "Baby moisturizing lotion bottle.", "default_storage_type": "ROOM", "image_url": None},
    {"name": "Dettol Antiseptic Liquid 250ml", "brand": "Dettol", "sku": "DETTOL-ANTISEPTIC-250ML", "barcode": "8901396389012", "barcode_type": "EAN13", "category": "Personal Care", "description": "Antiseptic disinfectant liquid.", "default_storage_type": "ROOM", "image_url": None},
]


def seed_products(session):
    created = 0
    skipped = 0

    for item in MOCK_PRODUCTS:
        existing = (
            session.query(Product)
            .filter((Product.sku == item["sku"]) | (Product.barcode == item["barcode"]))
            .first()
        )

        if existing:
            skipped += 1
            continue

        product = Product(**item)
        session.add(product)
        created += 1

    session.commit()
    return created, skipped


def main():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        created, skipped = seed_products(session)
        total = session.query(Product).count()

        print("Database seeded successfully.")
        print(f"Created products: {created}")
        print(f"Skipped existing products: {skipped}")
        print(f"Total products in database: {total}")
    finally:
        session.close()


if __name__ == "__main__":
    main()