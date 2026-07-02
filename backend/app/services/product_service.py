"""
services/product_service.py — Business logic for Product management.

All database access for products lives here.
Routes stay thin — they delegate to these functions and handle HTTP concerns.
"""

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.utils.exceptions import (
    ProductNotFoundError,
    DuplicateBarcodeError,
    DuplicateSKUError,
)


# ── Read ──────────────────────────────────────────────────────

def get_all_products(db: Session, skip: int = 0, limit: int = 50) -> list[Product]:
    """Return a paginated list of all products."""
    return db.query(Product).offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Product:
    """
    Return the product with the given ID.
    Raises ProductNotFoundError if not found.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return product


def get_product_by_barcode(db: Session, barcode: str) -> Product:
    """
    Return the product matching the barcode.
    Raises ProductNotFoundError if not found.
    """
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise ProductNotFoundError(f"No product with barcode {barcode}")
    return product


# ── Write ─────────────────────────────────────────────────────

def create_product(db: Session, data: ProductCreate) -> Product:
    """
    Create a new product.
    Raises DuplicateSKUError or DuplicateBarcodeError on conflicts.
    """
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise DuplicateSKUError(f"SKU '{data.sku}' is already registered")

    if db.query(Product).filter(Product.barcode == data.barcode).first():
        raise DuplicateBarcodeError(f"Barcode '{data.barcode}' is already registered")

    product = Product(
        name=data.name,
        sku=data.sku,
        barcode=data.barcode,
        category=data.category,
        image_url=data.image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    """
    Update fields on an existing product.
    Only provided (non-None) fields are changed.
    Raises ProductNotFoundError, DuplicateSKUError, or DuplicateBarcodeError.
    """
    product = get_product_by_id(db, product_id)   # raises if not found

    update_data = data.model_dump(exclude_unset=True)

    # Uniqueness checks for fields being updated
    if "sku" in update_data and update_data["sku"]:
        conflict = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id,
        ).first()
        if conflict:
            raise DuplicateSKUError(f"SKU '{update_data['sku']}' is already registered")

    if "barcode" in update_data and update_data["barcode"]:
        conflict = db.query(Product).filter(
            Product.barcode == update_data["barcode"],
            Product.id != product_id,
        ).first()
        if conflict:
            raise DuplicateBarcodeError(f"Barcode '{update_data['barcode']}' is already registered")

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    """
    Delete a product by ID.
    Raises ProductNotFoundError if the product does not exist.
    """
    product = get_product_by_id(db, product_id)   # raises if not found
    db.delete(product)
    db.commit()
