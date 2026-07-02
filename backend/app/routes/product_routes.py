"""
routes/product_routes.py — Product management API endpoints.

All routes return the standard envelope:
  Success: {"success": true,  "message": "...", "data": ...}
  Error:   {"success": false, "message": "...", "error_code": "..."}

Route order matters: static paths (/barcode/{barcode}) must come
before dynamic paths (/{product_id}) to prevent FastAPI matching
the literal string "barcode" as an integer product_id.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import (
    get_all_products,
    get_product_by_id,
    get_product_by_barcode,
    create_product,
    update_product,
    delete_product,
)
from app.utils.exceptions import (
    ProductNotFoundError,
    DuplicateBarcodeError,
    DuplicateSKUError,
)
from app.utils.response import success_response, error_response

router = APIRouter()


# ── POST /products ────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    try:
        product = create_product(db, payload)
        return success_response(
            data=ProductResponse.model_validate(product),
            message="Product created successfully",
        )
    except DuplicateSKUError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("A product with this SKU already exists", "DUPLICATE_SKU"),
        )
    except DuplicateBarcodeError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("A product with this barcode already exists", "DUPLICATE_BARCODE"),
        )


# ── GET /products ─────────────────────────────────────────────

@router.get("")
def list_products_endpoint(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Return a paginated list of all products."""
    products = get_all_products(db, skip=skip, limit=limit)
    return success_response(
        data=[ProductResponse.model_validate(p) for p in products],
        message="Products fetched successfully",
    )


# ── GET /products/barcode/{barcode} ──────────────────────────
# IMPORTANT: this must be registered BEFORE /{product_id} so FastAPI
# does not try to cast "barcode" as an integer.

@router.get("/barcode/{barcode}")
def get_by_barcode_endpoint(barcode: str, db: Session = Depends(get_db)):
    """Look up a product by its barcode."""
    try:
        product = get_product_by_barcode(db, barcode)
        return success_response(
            data=ProductResponse.model_validate(product),
            message="Product fetched successfully",
        )
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )


# ── GET /products/{product_id} ────────────────────────────────

@router.get("/{product_id}")
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    try:
        product = get_product_by_id(db, product_id)
        return success_response(
            data=ProductResponse.model_validate(product),
            message="Product fetched successfully",
        )
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )


# ── PUT /products/{product_id} ────────────────────────────────

@router.put("/{product_id}")
def update_product_endpoint(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
):
    """Update one or more fields on an existing product."""
    try:
        product = update_product(db, product_id, payload)
        return success_response(
            data=ProductResponse.model_validate(product),
            message="Product updated successfully",
        )
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )
    except DuplicateSKUError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("A product with this SKU already exists", "DUPLICATE_SKU"),
        )
    except DuplicateBarcodeError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("A product with this barcode already exists", "DUPLICATE_BARCODE"),
        )


# ── DELETE /products/{product_id} ─────────────────────────────

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    try:
        delete_product(db, product_id)
        return success_response(data=None, message="Product deleted successfully")
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )
