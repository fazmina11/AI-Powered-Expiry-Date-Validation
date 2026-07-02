from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.inventory import InventoryIntakeRequest, InventoryResponse
from app.services.inventory_service import intake, get_item, list_items
from app.utils.exceptions import ProductNotFoundError
from app.utils.response import success_response, error_response
from app.utils.constants import ACCEPTED, PRIORITY_SALE, REJECTED, MANUAL_REVIEW

router = APIRouter()


@router.post("/intake", status_code=status.HTTP_201_CREATED)
def intake_endpoint(data: InventoryIntakeRequest, db: Session = Depends(get_db)):
    try:
        item = intake(db, data)
        return success_response(InventoryResponse.model_validate(item))
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Product not found for this barcode", "PRODUCT_NOT_FOUND"),
        )


@router.get("")
def list_inventory_endpoint(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    items = list_items(db, skip=skip, limit=limit)
    return success_response([InventoryResponse.model_validate(i) for i in items])


# NOTE: All static string routes MUST be registered before /{item_id}
# to prevent FastAPI from matching "accepted", "rejected", etc. as integers.

@router.get("/accepted")
def list_accepted_items(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    items = list_items(db, status=ACCEPTED, skip=skip, limit=limit)
    return success_response([InventoryResponse.model_validate(i) for i in items])


@router.get("/priority-sale")
def list_priority_sale_items(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    items = list_items(db, status=PRIORITY_SALE, skip=skip, limit=limit)
    return success_response([InventoryResponse.model_validate(i) for i in items])


@router.get("/rejected")
def list_rejected_items(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    items = list_items(db, status=REJECTED, skip=skip, limit=limit)
    return success_response([InventoryResponse.model_validate(i) for i in items])


@router.get("/manual-review")
def list_manual_review_items(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    items = list_items(db, status=MANUAL_REVIEW, skip=skip, limit=limit)
    return success_response([InventoryResponse.model_validate(i) for i in items])


@router.get("/{item_id}")
def get_inventory_item_endpoint(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("Inventory item not found", "INVENTORY_ITEM_NOT_FOUND"),
        )
    return success_response(InventoryResponse.model_validate(item))
