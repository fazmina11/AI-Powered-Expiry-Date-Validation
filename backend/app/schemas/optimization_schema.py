"""
schemas/optimization_schema.py — Pydantic schemas for cost-benefit optimization responses.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class OptimizationResponse(BaseModel):
    """Result payload of the Cost-Benefit Optimization analysis."""
    recommended_action: str
    destination_warehouse_id: Optional[str] = None
    destination_warehouse_name: Optional[str] = None
    recommendation_ranking: List[Dict[str, Any]]
    recommendation_confidence: Decimal = Field(..., ge=0, le=100)
    action_scores: Dict[str, Decimal]
    current_inventory_value: Decimal = Field(..., ge=0)
    expected_recovery: Decimal = Field(..., ge=0)
    transport_cost: Decimal = Field(..., ge=0)
    net_benefit: Decimal
    loss_avoided: Decimal = Field(..., ge=0)
    roi_percent: Decimal
    recommendation_explanation: List[str]
    decision_engine_version: str

    model_config = ConfigDict(from_attributes=True)
