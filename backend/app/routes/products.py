from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.common import SuccessResponse
from app.services.product_service import (
    get_product_by_id,
    get_product_by_barcode,
    create_product,
    update_product,
    list_products,
)
from app.utils.exceptions import (
    ProductNotFoundError,
    DuplicateBarcodeError,
    DuplicateSKUError,
)
from app.utils.response import success_response, error_response

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product_in: ProductCreate, db: Session = Depends(get_db)):
    try:
        product = create_product(db, product_in)
        return success_response(ProductResponse.model_validate(product))
    except DuplicateSKUError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("SKU already exists", "DUPLICATE_SKU"),
        )
    except DuplicateBarcodeError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("Barcode already exists", "DUPLICATE_BARCODE"),
        )


@router.get("")
def list_products_endpoint(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    products = list_products(db, skip, limit)
    return success_response(
        [ProductResponse.model_validate(p) for p in products]
    )


@router.get("/{product_id}")
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )
    return success_response(ProductResponse.model_validate(product))


@router.get("/barcode/{barcode}")
def get_product_by_barcode_endpoint(barcode: str, db: Session = Depends(get_db)):
    product = get_product_by_barcode(db, barcode)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )
    return success_response(ProductResponse.model_validate(product))


@router.put("/{product_id}")
def update_product_endpoint(
    product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db)
):
    try:
        product = update_product(db, product_id, product_in)
        return success_response(ProductResponse.model_validate(product))
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found", "PRODUCT_NOT_FOUND"),
        )
    except DuplicateBarcodeError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("Barcode already exists", "DUPLICATE_BARCODE"),
        )
