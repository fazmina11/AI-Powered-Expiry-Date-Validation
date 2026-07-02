"""
schemas/inventory_schema.py — Pydantic schemas for the Inventory Intake system.

InventoryIntakeRequest  — POST /inventory/intake  request body
InventoryResponse       — single item response
InventoryListResponse   — list response wrapper
"""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, field_validator


class InventoryIntakeRequest(BaseModel):
    """
    Payload for POST /inventory/intake.

    barcode is required — used to resolve the Product.
    All date fields are optional; missing expiry_date triggers MANUAL_REVIEW.
    """
    barcode:            str
    batch_number:       str
    manufacturing_date: Optional[date] = None
    expiry_date:        Optional[date] = None

    @field_validator("barcode")
    @classmethod
    def barcode_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("barcode must not be blank")
        return v.strip()


class InventoryResponse(BaseModel):
    """Shape of a single InventoryItem returned to the client."""
    id:                 int
    product_id:         int
    batch_number:       Optional[str]
    manufacturing_date: Optional[date]
    expiry_date:        Optional[date]
    remaining_days:     Optional[int]
    status:             str
    decision_reason:    Optional[str]
    created_at:         datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryListResponse(BaseModel):
    """Paginated list of InventoryItem records."""
    total:  int
    items:  List[InventoryResponse]
