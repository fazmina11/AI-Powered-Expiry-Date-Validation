from datetime import date
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.inventory_item import InventoryItem
from app.models.barcode_scan import BarcodeScan
from app.schemas.database_schema import ProductCreate

router = APIRouter()


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    description: Optional[str] = None
    net_quantity: Optional[str] = None
    unit: Optional[str] = None
    mrp: Optional[float] = None
    currency: Optional[str] = None
    country_of_origin: Optional[str] = None
    product_type: Optional[str] = None
    default_storage_type: Optional[str] = None
    shelf_life_label: Optional[str] = None
    product_image_url: Optional[str] = None
    is_perishable: Optional[bool] = None


class InventoryIntakeRequest(BaseModel):
    barcode: str
    batch_number: str
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None


def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}


@router.get("/products")
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    data = []
    for p in products:
        data.append({
            "id": str(p.id),
            "name": p.name,
            "sku": p.sku,
            "barcode": p.barcode,
            "category": p.category,
            "image_url": p.image_url or p.product_image_url,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })
    return success_response(data, "Products fetched successfully")


@router.get("/products/barcode/{barcode}")
def get_by_barcode(barcode: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.barcode == barcode).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )
    data = {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "barcode": p.barcode,
        "category": p.category,
        "image_url": p.image_url or p.product_image_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    return success_response(data, "Product fetched successfully")


@router.get("/products/{product_id}")
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )
    data = {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "barcode": p.barcode,
        "category": p.category,
        "image_url": p.image_url or p.product_image_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    return success_response(data, "Product fetched successfully")


@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(
            status_code=409,
            detail={"message": "A product with this SKU already exists", "error_code": "DUPLICATE_SKU"}
        )
    if payload.barcode and db.query(Product).filter(Product.barcode == payload.barcode).first():
        raise HTTPException(
            status_code=409,
            detail={"message": "A product with this barcode already exists", "error_code": "DUPLICATE_BARCODE"}
        )

    p = Product(
        name=payload.name,
        brand=payload.brand,
        manufacturer=payload.manufacturer,
        sku=payload.sku,
        barcode=payload.barcode,
        barcode_type=payload.barcode_type,
        category=payload.category,
        sub_category=payload.sub_category,
        description=payload.description,
        net_quantity=payload.net_quantity,
        unit=payload.unit,
        mrp=payload.mrp,
        currency=payload.currency,
        country_of_origin=payload.country_of_origin,
        product_type=payload.product_type,
        default_storage_type=payload.default_storage_type,
        shelf_life_label=payload.shelf_life_label,
        product_image_url=payload.product_image_url,
        image_url=payload.product_image_url,
        is_perishable=payload.is_perishable,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    data = {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "barcode": p.barcode,
        "category": p.category,
        "image_url": p.image_url or p.product_image_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    return success_response(data, "Product created successfully")


@router.put("/products/{product_id}")
def update_product_endpoint(product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    data = {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "barcode": p.barcode,
        "category": p.category,
        "image_url": p.image_url or p.product_image_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    return success_response(data, "Product updated successfully")


@router.delete("/products/{product_id}")
def delete_product_endpoint(product_id: UUID, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )
    db.delete(p)
    db.commit()
    return success_response(None, "Product deleted successfully")


@router.get("/inventory")
def list_inventory(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    items = db.query(InventoryItem).offset(skip).limit(limit).all()
    total = db.query(InventoryItem).count()
    
    data_items = []
    for item in items:
        remaining_days = None
        if item.expiry_date:
            remaining_days = (item.expiry_date - date.today()).days

        data_items.append({
            "id": str(item.id),
            "product_id": str(item.product_id),
            "batch_number": item.batch_number,
            "manufacturing_date": item.manufacturing_date.isoformat() if item.manufacturing_date else None,
            "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
            "remaining_days": remaining_days,
            "status": item.operator_decision or item.intake_status or "PENDING",
            "decision_reason": item.notes or item.status_reason,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })
    return success_response({"total": total, "items": data_items}, "Inventory items fetched successfully")


@router.post("/inventory/intake", status_code=status.HTTP_201_CREATED)
def create_intake(payload: InventoryIntakeRequest, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.barcode == payload.barcode).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "No product found for this barcode", "error_code": "PRODUCT_NOT_FOUND"}
        )

    remaining_days = None
    status_val = "ACCEPTED"
    decision_reason = "Date is valid and product has sufficient shelf life."
    
    if payload.expiry_date:
        remaining_days = (payload.expiry_date - date.today()).days
        if remaining_days <= 0:
            status_val = "REJECTED"
            decision_reason = "Product has already expired."
        elif remaining_days <= 7:
            status_val = "PRIORITY_SALE"
            decision_reason = "Product nearing expiry; flagged for priority sale."
    else:
        status_val = "MANUAL_REVIEW"
        decision_reason = "Expiry date not detected or provided."

    scan = BarcodeScan(
        product_id=p.id,
        raw_barcode=payload.barcode,
        barcode_type=p.barcode_type,
        scan_source="WEB_CLIENT",
        scan_status="resolved",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    item = InventoryItem(
        product_id=p.id,
        barcode_scan_id=scan.id,
        batch_number=payload.batch_number,
        manufacturing_date=payload.manufacturing_date,
        expiry_date=payload.expiry_date,
        intake_source="MANUAL_ENTRY",
        intake_status=status_val,
        pipeline_status="ML_COMPLETED" if payload.expiry_date else "MANUAL_REVIEW",
        operator_decision=status_val,
        status_reason=decision_reason,
        notes=decision_reason,
        quantity=1,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    data = {
        "id": str(item.id),
        "product_id": str(item.product_id),
        "batch_number": item.batch_number,
        "manufacturing_date": item.manufacturing_date.isoformat() if item.manufacturing_date else None,
        "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
        "remaining_days": remaining_days,
        "status": item.operator_decision or item.intake_status,
        "decision_reason": item.notes or item.status_reason,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }
    return success_response(data, "Inventory item processed successfully")
