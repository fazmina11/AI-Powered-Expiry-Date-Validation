"""
community/routes/alert_routes.py
HTTP routes for PGN Community Safety Alert Engine (CSAE).
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.schemas.alert_schemas import (
    AlertResponse,
    AlertDashboardResponse,
)
from app.community.services import community_alert_service
from app.community.models.safety_alert import SafetyAlert, AlertHistory

router = APIRouter(prefix="/alerts", tags=["Community Safety Alert Engine"])


@router.get(
    "",
    response_model=List[AlertResponse],
    summary="List and filter safety alerts",
)
def list_alerts(
    alert_level: Optional[str] = Query(None, description="Filter by alert level (WARNING, CRITICAL, etc)"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, RESOLVED, etc)"),
    risk_score: Optional[int] = Query(None, description="Filter alerts with risk greater or equal"),
    cluster_id: Optional[uuid.UUID] = Query(None, description="Filter by associated issue cluster ID"),
    severity: Optional[str] = Query(None, description="Filter by cluster severity level"),
    date_from: Optional[datetime] = Query(None, description="Filter alerts generated since this datetime"),
    date_to: Optional[datetime] = Query(None, description="Filter alerts generated until this datetime"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[AlertResponse]:
    """Get all safety alerts matching specified filters."""
    return community_alert_service.list_alerts(
        db,
        alert_level=alert_level,
        status=status,
        risk_score=risk_score,
        cluster_id=cluster_id,
        severity=severity,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/active",
    response_model=List[AlertResponse],
    summary="List all active safety alerts",
)
def get_active_alerts(
    db: Session = Depends(get_db),
) -> List[AlertResponse]:
    """Retrieve all safety alerts currently in the ACTIVE status."""
    return db.query(SafetyAlert).filter(SafetyAlert.status == "ACTIVE").order_by(
        SafetyAlert.risk_score.desc()
    ).all()


@router.get(
    "/high-risk",
    response_model=List[AlertResponse],
    summary="List high-risk and critical safety alerts",
)
def get_high_risk_alerts(
    db: Session = Depends(get_db),
) -> List[AlertResponse]:
    """Retrieve all safety alerts categorized as HIGH_RISK or CRITICAL alert levels."""
    return db.query(SafetyAlert).filter(SafetyAlert.alert_level.in_(["HIGH_RISK", "CRITICAL"])).order_by(
        SafetyAlert.risk_score.desc()
    ).all()


@router.get(
    "/dashboard",
    response_model=AlertDashboardResponse,
    summary="Get safety alerts dashboard statistics",
)
def get_alerts_dashboard(
    db: Session = Depends(get_db),
) -> AlertDashboardResponse:
    """Compile safety alerts metrics: active count, resolution averages, and priority summaries."""
    return community_alert_service.get_dashboard_statistics(db)


@router.post(
    "/recalculate",
    summary="Force recalculation and evaluation of alerts for all clusters",
)
def recalculate_alerts(
    db: Session = Depends(get_db),
):
    """Trigger manual re-evaluation of safety alerts threshold rules for all issue clusters."""
    processed = community_alert_service.recalculate_all_alerts(db)
    return {
        "success": True,
        "message": f"Successfully re-evaluated threshold safety rules for {processed} issue clusters.",
        "processed_clusters_count": processed,
    }


@router.get(
    "/code/{alert_code}",
    response_model=AlertResponse,
    summary="Get single safety alert by unique code",
    responses={404: {"description": "Alert not found"}},
)
def get_alert_by_code(
    alert_code: str,
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Fetch safety alert profile using its unique code (e.g. CSA-2026-000001)."""
    alert = db.query(SafetyAlert).filter(SafetyAlert.alert_code == alert_code).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ALERT_NOT_FOUND",
                "message": f"Safety alert with code '{alert_code}' not found.",
            },
        )
    return alert


@router.get(
    "/{id}",
    response_model=AlertResponse,
    summary="Get single safety alert by ID",
    responses={404: {"description": "Alert not found"}},
)
def get_alert_by_id(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Fetch safety alert details by UUID."""
    return community_alert_service.get_alert(db, id)


@router.patch(
    "/{id}/acknowledge",
    response_model=AlertResponse,
    summary="Acknowledge an active safety alert",
)
def acknowledge_alert(
    id: uuid.UUID,
    remarks: Optional[str] = Query(None, description="Custom acknowledgement remarks"),
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Transition a safety alert status from ACTIVE to ACKNOWLEDGED."""
    alert = community_alert_service.get_alert(db, id)
    if alert.status not in ("ACTIVE", "UNDER_INVESTIGATION"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition alert from status '{alert.status}' to 'ACKNOWLEDGED'."
        )
        
    old_status = alert.status
    alert.status = "ACKNOWLEDGED"
    history = AlertHistory(
        alert_id=alert.id,
        old_status=old_status,
        new_status="ACKNOWLEDGED",
        remarks=remarks or "Alert acknowledged.",
        changed_by="SYSTEM",
    )
    db.add(history)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch(
    "/{id}/resolve",
    response_model=AlertResponse,
    summary="Mark safety alert as resolved",
)
def resolve_alert(
    id: uuid.UUID,
    remarks: Optional[str] = Query(None, description="Resolution details"),
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Transition safety alert to the RESOLVED state, logging resolution timestamps."""
    return community_alert_service.resolve_alert(db, id, remarks)


@router.patch(
    "/{id}/close",
    response_model=AlertResponse,
    summary="Mark safety alert as closed",
)
def close_alert(
    id: uuid.UUID,
    remarks: Optional[str] = Query(None, description="Closure notes"),
    db: Session = Depends(get_db),
) -> AlertResponse:
    """Transition safety alert to the CLOSED state."""
    return community_alert_service.close_alert(db, id, remarks)
