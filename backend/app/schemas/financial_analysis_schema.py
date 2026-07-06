"""
schemas/financial_analysis_schema.py — Pydantic schemas for Financial Decision Engine results.
"""

from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class FinancialAnalysisResponse(BaseModel):
    """Result payload of the standalone financial risk assessment."""
    inventory_item_id: int
    inventory_cost: Decimal = Field(..., ge=0)
    potential_revenue: Decimal = Field(..., ge=0)
    potential_financial_loss: Decimal = Field(..., ge=0)
    supplier_recoverable_value: Decimal = Field(..., ge=0)
    maximum_recoverable_value: Decimal = Field(..., ge=0)
    financial_health_score: Decimal = Field(..., ge=0, le=100)
    financial_status: str
    financial_priority: str
    financial_explanations: List[str]
    decision_ready: bool

    model_config = ConfigDict(from_attributes=True)
