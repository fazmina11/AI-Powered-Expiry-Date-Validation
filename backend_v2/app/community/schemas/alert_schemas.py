"""
community/schemas/alert_schemas.py
Pydantic schemas for PGN Community Safety Alert Engine (CSAE).
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class AlertHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    alert_id: uuid.UUID
    old_status: Optional[str] = None
    new_status: str
    remarks: Optional[str] = None
    changed_by: str
    created_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    alert_code: str
    cluster_id: uuid.UUID
    alert_level: str
    status: str
    title: str
    description: str
    recommended_action: str
    generated_reason: str
    generated_by: str
    risk_score: int
    affected_reports: int
    affected_users: int
    affected_cities: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    history: List[AlertHistoryResponse] = []


class AlertDashboardResponse(BaseModel):
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    resolved_alerts: int
    newest_alert: Optional[AlertResponse] = None
    highest_risk_alert: Optional[AlertResponse] = None
    average_resolution_time: float  # average resolution time in hours


class AlertSummary(BaseModel):
    level: str
    status: str
    count: int
