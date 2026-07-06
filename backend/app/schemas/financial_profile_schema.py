"""
schemas/financial_profile_schema.py — Pydantic schemas for ProductFinancialProfile CRUD.

ProductFinancialProfileCreate  — payload for POST /financial-profiles
ProductFinancialProfileUpdate  — payload for PUT /financial-profiles/{product_id}
ProductFinancialProfileResponse — response shape returned to the client
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from pydantic import BaseModel, Field, model_validator, ConfigDict


class ProductFinancialProfileCreate(BaseModel):
    product_id: int
    purchase_price: Decimal = Field(..., gt=0)
    mrp: Decimal = Field(..., gt=0)
    default_profit_margin_percent: Decimal = Field(..., ge=0, le=100)
    currency: str = Field(default="INR", min_length=1, max_length=10)
    supplier_return_allowed: bool = Field(default=True)
    supplier_return_percent: Decimal = Field(default=100.00, ge=0, le=100)

    @model_validator(mode="after")
    def validate_mrp_gte_purchase_price(self) -> "ProductFinancialProfileCreate":
        if self.mrp < self.purchase_price:
            raise ValueError("MRP must be greater than or equal to purchase price")
        return self


class ProductFinancialProfileUpdate(BaseModel):
    """All fields optional — only provided fields are updated (PATCH/PUT semantics)."""
    purchase_price: Optional[Decimal] = Field(default=None, gt=0)
    mrp: Optional[Decimal] = Field(default=None, gt=0)
    default_profit_margin_percent: Optional[Decimal] = Field(default=None, ge=0, le=100)
    currency: Optional[str] = Field(default=None, min_length=1, max_length=10)
    supplier_return_allowed: Optional[bool] = Field(default=None)
    supplier_return_percent: Optional[Decimal] = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def validate_mrp_gte_purchase_price(self) -> "ProductFinancialProfileUpdate":
        if self.mrp is not None and self.purchase_price is not None:
            if self.mrp < self.purchase_price:
                raise ValueError("MRP must be greater than or equal to purchase price")
        return self


class ProductFinancialProfileResponse(BaseModel):
    id: uuid.UUID
    product_id: int
    purchase_price: Decimal
    mrp: Decimal
    default_profit_margin_percent: Decimal
    currency: str
    supplier_return_allowed: bool
    supplier_return_percent: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
