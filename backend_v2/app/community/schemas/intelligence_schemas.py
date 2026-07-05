"""
community/schemas/intelligence_schemas.py
Pydantic schemas for PGN Community Intelligence Engine (CIE).
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.community.schemas.cluster_schemas import IssueClusterResponse


class ClusterIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cluster_id: uuid.UUID
    risk_score: int
    growth_rate: float
    activity_level: str
    trend: str
    spread_level: str
    escalation_level: str
    reports_last_24h: int
    reports_last_7_days: int
    reports_last_30_days: int
    new_cities: int
    average_credibility: float
    is_trending: bool
    last_calculated: datetime


class ClusterDashboardResponse(BaseModel):
    highest_risk: Optional[IssueClusterResponse] = None
    fastest_growing: Optional[IssueClusterResponse] = None
    most_active: Optional[IssueClusterResponse] = None
    newest_cluster: Optional[IssueClusterResponse] = None
    dormant_clusters: List[IssueClusterResponse] = []


class ClusterTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cluster_id: uuid.UUID
    cluster_code: str
    barcode: str
    growth_rate: float
    is_trending: bool
