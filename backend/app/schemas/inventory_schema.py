"""
schemas/inventory_schema.py — Pydantic schemas for the Inventory Intake system.

InventoryIntakeRequest  — POST /inventory/intake  request body
InventoryResponse       — single item response
InventoryListResponse   — list response wrapper
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict, field_validator, Field


class InventoryIntakeRequest(BaseModel):
    """
    Payload for POST /inventory/intake.

    barcode is required — used to resolve the Product.
    All date fields are optional; missing expiry_date triggers MANUAL_REVIEW.
    mrp, quantity, and purchase_price are optional for financial autonomy (Phase 2).
    """
    barcode:            str
    batch_number:       str
    manufacturing_date: Optional[date] = None
    expiry_date:        Optional[date] = None
    mrp:                Optional[Decimal] = Field(default=None, gt=0)
    quantity:           Optional[int] = Field(default=1, gt=0)
    purchase_price:     Optional[Decimal] = Field(default=None, gt=0)

    @field_validator("barcode")
    @classmethod
    def barcode_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("barcode must not be blank")
        return v.strip()


class InventoryResponse(BaseModel):
    """Shape of a single InventoryItem returned to the client."""
    id:                         int
    product_id:                 int
    batch_number:               Optional[str]
    manufacturing_date:         Optional[date]
    expiry_date:                Optional[date]
    remaining_days:             Optional[int]
    status:                     str
    decision_reason:            Optional[str]
    created_at:                 datetime

    # Financial fields (Phase 2)
    quantity:                   int
    purchase_price:             Optional[Decimal]
    mrp:                        Optional[Decimal]
    inventory_cost:             Optional[Decimal]
    currency:                   str
    supplier_return_allowed:    Optional[bool]
    supplier_return_percent:    Optional[Decimal]
    financial_profile_snapshot: Optional[Any]

    model_config = ConfigDict(from_attributes=True)


class InventoryListResponse(BaseModel):
    """Paginated list of InventoryItem records."""
    total:  int
    items:  List[InventoryResponse]
