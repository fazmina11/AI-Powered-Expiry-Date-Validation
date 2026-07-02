"""
schemas/dashboard_schema.py — Pydantic response schemas for dashboard endpoints.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ── Summary ───────────────────────────────────────────────────

class DashboardSummaryResponse(BaseModel):
    total_products:          int
    total_inventory_items:   int
    accepted_count:          int
    priority_sale_count:     int
    rejected_count:          int
    manual_review_count:     int
    invalid_date_count:      int
    valid_validation_count:  int
    low_confidence_count:    int


# ── Breakdowns ────────────────────────────────────────────────

class InventoryBreakdownResponse(BaseModel):
    accepted:      int
    priority_sale: int
    rejected:      int
    manual_review: int
    invalid_date:  int


class ValidationBreakdownResponse(BaseModel):
    valid:          int
    low_confidence: int
    manual_review:  int


# ── Recent activity items ─────────────────────────────────────

class RecentInventoryItem(BaseModel):
    id:                 int
    product_id:         int
    batch_number:       Optional[str]
    expiry_date:        Optional[date]
    remaining_days:     Optional[int]
    status:             str
    decision_reason:    Optional[str]
    created_at:         datetime

    model_config = ConfigDict(from_attributes=True)


class RecentValidationItem(BaseModel):
    id:                    int
    inventory_item_id:     int
    validation_status:     str
    confidence_score:      Optional[float]
    extracted_expiry_date: Optional[date]
    created_at:            datetime

    model_config = ConfigDict(from_attributes=True)


# ── Alerts ────────────────────────────────────────────────────

class AlertItem(BaseModel):
    id:              int
    product_id:      int
    batch_number:    Optional[str]
    expiry_date:     Optional[date]
    remaining_days:  Optional[int]
    status:          str
    decision_reason: Optional[str]
    created_at:      datetime

    model_config = ConfigDict(from_attributes=True)


class AlertsResponse(BaseModel):
    count: int
    items: List[AlertItem]
