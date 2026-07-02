"""
schemas/product_schema.py — Pydantic schemas for Product CRUD.

ProductCreate  — payload for POST /products
ProductUpdate  — payload for PUT /products/{id}  (all fields optional)
ProductResponse — response shape returned to the client
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name:      str
    sku:       str
    barcode:   str                   # required — must be unique
    category:  Optional[str] = None
    image_url: Optional[str] = None  # ML/OCR placeholder for future phases


class ProductUpdate(BaseModel):
    """All fields optional — only provided fields are updated (PATCH semantics)."""
    name:      Optional[str] = None
    sku:       Optional[str] = None
    barcode:   Optional[str] = None
    category:  Optional[str] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id:         int
    name:       str
    sku:        str
    barcode:    str
    category:   Optional[str]
    image_url:  Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
