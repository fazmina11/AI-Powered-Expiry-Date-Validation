"""
community/schemas/investigation_schemas.py
Pydantic schemas for PGN Investigation & Case Management Engine (ICME).
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict


class CaseNoteCreate(BaseModel):
    note: str
    created_by: Optional[str] = "SYSTEM"


class CaseNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    note: str
    created_by: str
    created_at: datetime


class CaseEvidenceCreate(BaseModel):
    evidence_type: str  # IMAGE, DOCUMENT, RECEIPT, LAB_REPORT, VIDEO, OTHER
    file_url: str
    description: str
    uploaded_by: Optional[str] = "SYSTEM"


class CaseEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    evidence_type: str
    file_url: str
    description: str
    uploaded_by: str
    uploaded_at: datetime


class TimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    event_type: str
    event_description: str
    performed_by: str
    created_at: datetime


class CaseCreate(BaseModel):
    alert_id: uuid.UUID
    title: str
    description: str
    due_date: Optional[datetime] = None
    priority: Optional[str] = "MEDIUM"


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_number: str
    alert_id: uuid.UUID
    cluster_id: uuid.UUID
    assigned_officer: Optional[str] = None
    priority: str
    status: str
    title: str
    description: str
    opened_at: datetime
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    resolution: Optional[str] = None
    final_decision: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    notes: List[CaseNoteResponse] = []
    evidence: List[CaseEvidenceResponse] = []
    timeline: List[TimelineResponse] = []


class CaseSummary(BaseModel):
    priority: str
    status: str
    count: int


class CaseDashboardResponse(BaseModel):
    total_cases: int
    open_cases: int
    critical_cases: int
    assigned_cases: int
    average_resolution_time: float  # resolution time in hours
    cases_by_priority: Dict[str, int]
    cases_by_status: Dict[str, int]
    newest_case: Optional[CaseResponse] = None
    oldest_open_case: Optional[CaseResponse] = None
