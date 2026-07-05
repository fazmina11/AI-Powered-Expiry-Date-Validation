"""
community/routes/case_routes.py
HTTP routes for PGN Investigation & Case Management Engine (ICME).
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.schemas.investigation_schemas import (
    CaseCreate,
    CaseResponse,
    CaseNoteCreate,
    CaseNoteResponse,
    CaseEvidenceCreate,
    CaseEvidenceResponse,
    TimelineResponse,
    CaseDashboardResponse,
)
from app.community.services import investigation_service
from app.community.models.investigation import CaseTimeline

router = APIRouter(prefix="/cases", tags=["Investigation & Case Management Engine"])


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new investigation case",
)
def create_investigation_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Spin up a case for an alert matching rules (alert is HIGH_RISK or CRITICAL)."""
    return investigation_service.create_case(
        db,
        alert_id=payload.alert_id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        priority=payload.priority or "MEDIUM",
    )


@router.get(
    "",
    response_model=List[CaseResponse],
    summary="List and filter investigation cases",
)
def list_investigation_cases(
    priority: Optional[str] = Query(None, description="Filter by priority (LOW, MEDIUM, HIGH, CRITICAL)"),
    status: Optional[str] = Query(None, description="Filter by status (OPEN, ASSIGNED, UNDER_INVESTIGATION, etc)"),
    assigned_officer: Optional[str] = Query(None, description="Filter by assigned officer"),
    cluster_id: Optional[uuid.UUID] = Query(None, description="Filter by cluster ID"),
    alert_id: Optional[uuid.UUID] = Query(None, description="Filter by safety alert ID"),
    date_from: Optional[datetime] = Query(None, description="Filter cases created since this datetime"),
    date_to: Optional[datetime] = Query(None, description="Filter cases created until this datetime"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[CaseResponse]:
    """Get all investigation cases matching specified filters."""
    return investigation_service.list_cases(
        db,
        priority=priority,
        status=status,
        assigned_officer=assigned_officer,
        cluster_id=cluster_id,
        alert_id=alert_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/dashboard",
    response_model=CaseDashboardResponse,
    summary="Get cases dashboard statistics",
)
def get_cases_dashboard(
    db: Session = Depends(get_db),
) -> CaseDashboardResponse:
    """Compile case dashboard KPIs: open, critical, resolution time average, priority/status stats."""
    return investigation_service.get_dashboard_statistics(db)


@router.get(
    "/{id}",
    response_model=CaseResponse,
    summary="Get single investigation case by ID",
    responses={404: {"description": "Case not found"}},
)
def get_case_by_id(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Fetch investigation case details by UUID."""
    return investigation_service.get_case(db, id)


@router.patch(
    "/{id}/assign",
    response_model=CaseResponse,
    summary="Assign a case to an officer",
)
def assign_investigation_case(
    id: uuid.UUID,
    officer: str = Query(..., min_length=1, description="Officer name/identifier"),
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Assign case to a designated officer. Sets status to ASSIGNED if current status is OPEN."""
    return investigation_service.assign_case(db, id, officer)


@router.patch(
    "/{id}/status",
    response_model=CaseResponse,
    summary="Update case status",
)
def update_case_status(
    id: uuid.UUID,
    status: str = Query(..., description="Target status (UNDER_INVESTIGATION, WAITING_FOR_INFORMATION, etc)"),
    remarks: Optional[str] = Query(None, description="Transition notes"),
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Transition case status and record timeline logs."""
    return investigation_service.update_status(db, id, status, remarks)


@router.patch(
    "/{id}/resolve",
    response_model=CaseResponse,
    summary="Mark case as resolved",
)
def resolve_investigation_case(
    id: uuid.UUID,
    resolution: str = Query(..., min_length=10, description="Detailed resolution summary"),
    final_decision: str = Query(..., description="Decision enum (RECOMMEND_RECALL, CONTINUE_MONITORING, etc)"),
    performed_by: str = Query("SYSTEM", description="Entity performing resolution"),
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Mark investigation case as RESOLVED and compile decision details."""
    return investigation_service.resolve_case(db, id, resolution, final_decision, performed_by)


@router.patch(
    "/{id}/close",
    response_model=CaseResponse,
    summary="Mark case as closed",
)
def close_investigation_case(
    id: uuid.UUID,
    performed_by: str = Query("SYSTEM", description="Entity closing case"),
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Close investigation case. Automatically closes safety alert if cluster risk is resolved."""
    return investigation_service.close_case(db, id, performed_by)


@router.post(
    "/{id}/notes",
    response_model=CaseNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add note log to case folder",
)
def add_case_note(
    id: uuid.UUID,
    payload: CaseNoteCreate,
    db: Session = Depends(get_db),
) -> CaseNoteResponse:
    """Append a textual note log to the investigation timeline history."""
    return investigation_service.add_note(db, id, payload.note, payload.created_by or "SYSTEM")


@router.post(
    "/{id}/evidence",
    response_model=CaseEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attach evidence URL to case folder",
)
def attach_case_evidence(
    id: uuid.UUID,
    payload: CaseEvidenceCreate,
    db: Session = Depends(get_db),
) -> CaseEvidenceResponse:
    """Attach evidence file URLs and logs to the case folder."""
    return investigation_service.upload_evidence(
        db,
        case_id=id,
        evidence_type=payload.evidence_type,
        file_url=payload.file_url,
        description=payload.description,
        uploaded_by=payload.uploaded_by or "SYSTEM",
    )


@router.get(
    "/{id}/timeline",
    response_model=List[TimelineResponse],
    summary="Get case timeline audit logs",
)
def get_case_timeline(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> List[TimelineResponse]:
    """Retrieve audit timeline logs chronologically for the specified case."""
    # Ensure case exists
    investigation_service.get_case(db, id)
    return db.query(CaseTimeline).filter(CaseTimeline.case_id == id).order_by(
        CaseTimeline.created_at.asc()
    ).all()
