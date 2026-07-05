from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.product import Product

router = APIRouter()

def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}

def _product_to_dict(p: Product) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "barcode": p.barcode,
        "category": p.category,
        "brand": p.brand,
        "description": p.description,
        "mrp": float(p.mrp) if p.mrp is not None else None,
        "warehouse_location": p.warehouse_location,
        "is_perishable": p.is_perishable,
        "image_url": p.image_url or p.product_image_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }

class ProductCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    sku: Optional[str] = None
    barcode: str
    category: Optional[str] = None
    description: Optional[str] = None
    mrp: Optional[float] = None
    is_perishable: Optional[bool] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    warehouse_location: Optional[str] = None
    description: Optional[str] = None
    mrp: Optional[float] = None
    is_perishable: Optional[bool] = None

@router.get("/")
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return success_response([_product_to_dict(p) for p in products], "Products fetched successfully")

@router.get("/barcode/{barcode}")
def get_by_barcode(barcode: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.barcode == barcode).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )
    return success_response(_product_to_dict(p), "Product fetched successfully")

@router.get("/{product_id}")
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )
    return success_response(_product_to_dict(p), "Product fetched successfully")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.barcode == payload.barcode).first():
        raise HTTPException(status_code=400, detail="Barcode already exists")
    
    p = Product(
        name=payload.name,
        brand=payload.brand,
        sku=payload.sku,
        barcode=payload.barcode,
        category=payload.category,
        description=payload.description,
        mrp=payload.mrp,
        is_perishable=payload.is_perishable
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return success_response(_product_to_dict(p), "Product created successfully")

@router.patch("/{product_id}")
def update_product(product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return success_response(_product_to_dict(p), "Product updated successfully")
